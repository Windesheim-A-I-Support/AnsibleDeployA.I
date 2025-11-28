#!/usr/bin/env python3
"""
Validate Ansible playbooks for realistic deployment
Checks for common issues without requiring Ansible installation
"""

import yaml
import re
import sys
from pathlib import Path

def color(text, code):
    """ANSI color codes"""
    return f"\033[{code}m{text}\033[0m"

def success(text):
    return color(f"✅ {text}", "92")

def warning(text):
    return color(f"⚠️  {text}", "93")

def error(text):
    return color(f"❌ {text}", "91")

def info(text):
    return color(f"ℹ️  {text}", "94")

class PlaybookValidator:
    def __init__(self, playbook_path):
        self.playbook_path = Path(playbook_path)
        self.issues = []
        self.warnings = []
        self.content = None

    def load(self):
        """Load playbook content"""
        try:
            with open(self.playbook_path, 'r') as f:
                self.content = f.read()
            return True
        except Exception as e:
            self.issues.append(f"Cannot read file: {e}")
            return False

    def check_yaml_syntax(self):
        """Check if YAML is valid"""
        try:
            yaml.safe_load(self.content)
            print(success("YAML syntax is valid"))
            return True
        except yaml.YAMLError as e:
            self.issues.append(f"YAML syntax error: {e}")
            return False

    def check_docker_images(self):
        """Extract and validate Docker images"""
        # Find all image references
        image_pattern = r'image:\s+([^\s]+)'
        images = re.findall(image_pattern, self.content)

        if not images:
            self.warnings.append("No Docker images found in playbook")
            return False

        print(info(f"Found {len(images)} Docker images"))

        # Check for common image issues
        for img in images:
            # Check for variables that need substitution
            if '${' in img or '{{' in img:
                continue  # Variables are fine

            # Check for valid image format
            if ':' not in img and img != 'postgres' and img != 'redis':
                self.warnings.append(f"Image '{img}' missing tag (will use :latest)")

            print(f"  - {img}")

        print(success(f"Docker images look valid"))
        return True

    def check_port_conflicts(self):
        """Check for potential port conflicts"""
        port_pattern = r'["\'](\d+):\d+["\']'
        ports = re.findall(port_pattern, self.content)

        if ports:
            unique_ports = set(ports)
            if len(ports) != len(unique_ports):
                self.warnings.append("Potential port conflicts detected")
            print(info(f"Found {len(unique_ports)} unique external ports"))
            return True
        return False

    def check_required_vars(self):
        """Check for undefined variables"""
        # Find all variable references
        var_pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}'
        vars_used = set(re.findall(var_pattern, self.content))

        if vars_used:
            print(info(f"Found {len(vars_used)} variables used"))

            # Check if vars are defined in inventory or playbook
            common_vars = {'ansible_host', 'ansible_user', 'base_domain',
                          'ai_admin_user', 'ansible_date_time'}

            undefined = vars_used - common_vars
            if undefined:
                print(warning(f"Variables may need definition in inventory: {', '.join(list(undefined)[:5])}"))

        return True

    def check_ansible_modules(self):
        """Check for realistic Ansible module usage"""
        modules = re.findall(r'^\s+([a-z_]+):\s*$', self.content, re.MULTILINE)

        # Common modules that require collections
        collection_modules = {
            'docker_compose': 'community.docker',
            'docker_container': 'community.docker',
            'docker_image': 'community.docker',
        }

        missing_collections = set()
        for module in modules:
            if module in collection_modules:
                missing_collections.add(collection_modules[module])

        if missing_collections:
            print(warning(f"Requires collections: {', '.join(missing_collections)}"))

        return True

    def check_realistic_resources(self):
        """Check for realistic resource allocations"""
        # Check memory allocations
        mem_pattern = r'memory["\s:]*(\d+)[GM]'
        memory_values = re.findall(mem_pattern, self.content, re.IGNORECASE)

        if memory_values:
            total_mem = sum(int(m) for m in memory_values)
            if total_mem > 64:
                self.warnings.append(f"Total memory allocation ({total_mem}GB) may be high for single host")

        return True

    def check_docker_compose_embedded(self):
        """Check embedded docker-compose.yml syntax"""
        # Find docker-compose content in playbook
        compose_start = self.content.find('content: |')
        if compose_start == -1:
            return True  # No embedded compose file

        # Extract compose content
        lines = self.content[compose_start:].split('\n')
        compose_lines = []
        in_compose = False

        for line in lines:
            if 'version:' in line:
                in_compose = True

            if in_compose:
                # Remove YAML indentation (usually 10 spaces for content: |)
                clean_line = line[10:] if len(line) > 10 and line[:10] == ' ' * 10 else line
                compose_lines.append(clean_line)

                # Stop at next Ansible task
                if line.strip().startswith('- name:') and len(compose_lines) > 10:
                    break

        compose_content = '\n'.join(compose_lines)

        # Try to parse as YAML
        try:
            compose_yaml = yaml.safe_load(compose_content)
            if compose_yaml and 'services' in compose_yaml:
                print(success(f"Embedded docker-compose.yml is valid"))
                print(info(f"  Services: {', '.join(compose_yaml['services'].keys())}"))

                # Check each service
                for svc_name, svc_config in compose_yaml['services'].items():
                    if 'image' not in svc_config:
                        self.warnings.append(f"Service '{svc_name}' missing image")
                    if 'restart' not in svc_config:
                        self.warnings.append(f"Service '{svc_name}' missing restart policy")

                return True
        except yaml.YAMLError as e:
            self.issues.append(f"Embedded docker-compose.yml syntax error: {e}")
            return False

        return True

    def validate(self):
        """Run all validation checks"""
        print(f"\n{'='*60}")
        print(f"Validating: {self.playbook_path.name}")
        print(f"{'='*60}\n")

        if not self.load():
            return False

        checks = [
            self.check_yaml_syntax,
            self.check_docker_images,
            self.check_port_conflicts,
            self.check_required_vars,
            self.check_ansible_modules,
            self.check_realistic_resources,
            self.check_docker_compose_embedded,
        ]

        for check in checks:
            try:
                check()
            except Exception as e:
                self.issues.append(f"Check failed: {check.__name__}: {e}")

        # Print summary
        print(f"\n{'='*60}")
        print("VALIDATION SUMMARY")
        print(f"{'='*60}\n")

        if self.issues:
            print(error(f"Found {len(self.issues)} critical issues:"))
            for issue in self.issues:
                print(f"  ❌ {issue}")
            print()

        if self.warnings:
            print(warning(f"Found {len(self.warnings)} warnings:"))
            for warn in self.warnings:
                print(f"  ⚠️  {warn}")
            print()

        if not self.issues:
            if not self.warnings:
                print(success("Playbook validation passed with no issues!"))
            else:
                print(success("Playbook validation passed (with warnings)"))
            return True
        else:
            print(error("Playbook validation FAILED"))
            return False

def main():
    ansible_dir = Path(__file__).parent

    # Find all playbooks
    playbooks = list(ansible_dir.glob('*.yml'))
    playbooks = [p for p in playbooks if not p.name.startswith('inventory')]

    if not playbooks:
        print(error("No playbooks found in directory"))
        return 1

    print(f"\n{'#'*60}")
    print("# ANSIBLE PLAYBOOK VALIDATOR")
    print(f"# Found {len(playbooks)} playbook(s) to validate")
    print(f"{'#'*60}")

    results = {}
    for playbook in sorted(playbooks):
        validator = PlaybookValidator(playbook)
        results[playbook.name] = validator.validate()

    # Final summary
    print(f"\n{'#'*60}")
    print("# FINAL SUMMARY")
    print(f"{'#'*60}\n")

    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed

    for name, result in sorted(results.items()):
        status = success("PASS") if result else error("FAIL")
        print(f"{status} - {name}")

    print(f"\n{success(f'Passed: {passed}')} | {error(f'Failed: {failed}')}")

    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
