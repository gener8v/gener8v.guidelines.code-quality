import unittest

from cq_measure.fixture_repository import findings_for


def flagged(files: dict[str, str], config: dict | None = None) -> list[str]:
    return sorted(f.path for f in findings_for(files, "package-by-layer", config))


class DomainFirstTest(unittest.TestCase):
    def test_roles_and_layers_at_the_top_fail(self):
        files = {"src/controllers/a.ts": "", "src/services/b.ts": "", "src/logging/c.ts": "", "src/billing/d.ts": ""}
        found = findings_for(files, "package-by-layer")
        self.assertEqual(sorted(f.path for f in found), ["src/controllers", "src/logging", "src/services"])
        self.assertTrue(all(f.severity == "fail" for f in found))

    def test_roles_below_a_domain_pass(self):
        files = {
            "src/accounting/disputes/services/a.ts": "",
            "src/accounting/disputes/routes/b.ts": "",
            "src/accounting/discrepancies/models/c.ts": "",
            "src/billing/d.ts": "",
        }
        self.assertEqual(flagged(files), [])

    def test_mechanism_directories_are_not_the_top(self):
        java = {"src/main/java/com/acme/shop/web/A.java": "", "src/main/java/com/acme/shop/customer/web/B.java": ""}
        self.assertEqual(flagged(java), ["src/main/java/com/acme/shop/web"])
        self.assertEqual(flagged({"internal/handlers/h.go": "", "cmd/server/main.go": ""}), ["internal/handlers"])
        python = {"src/mytool/__init__.py": "", "src/mytool/checks/a.py": "", "src/mytool/core/b.py": ""}
        self.assertEqual(flagged(python), ["src/mytool/core"])

    def test_a_single_domain_with_code_is_a_domain(self):
        files = {"frontend/src/fleet/FleetApp.tsx": "", "frontend/src/fleet/components/Chip.tsx": ""}
        self.assertEqual(flagged(files), ["frontend"])

    def test_layer_projects_fail_and_bounded_context_projects_pass(self):
        files = {"src/Infrastructure/Db.cs": "", "src/Ordering.Domain/Order.cs": "", "src/Ordering.Api/Api.cs": ""}
        self.assertEqual(flagged(files), ["src/Infrastructure"])

    def test_each_package_of_a_monorepo_has_its_own_top(self):
        files = {"packages/storefront/package.json": "{}", "packages/storefront/src/components/a.tsx": "", "packages/web/b.ts": ""}
        self.assertEqual(flagged(files), ["packages/storefront/src/components", "packages/web"])

    def test_url_routes_tests_and_scripts_are_not_code_groupings(self):
        files = {"app/api/route.ts": "", "src/routes/+page.ts": "", "tests/services/a_test.py": "", "scripts/db/seed.py": ""}
        self.assertEqual(flagged(files), [])

    def test_a_route_file_outside_a_route_tree_is_no_exemption(self):
        self.assertEqual(flagged({"server/src/route.ts": "", "server/src/app.ts": ""}), ["server"])

    def test_configuration_adds_role_names(self):
        self.assertEqual(flagged({"src/gizmos/a.ts": ""}, {"checks": {"package-by-layer": {"role_dirs": ["gizmos"]}}}), ["src/gizmos"])


if __name__ == "__main__":
    unittest.main()
