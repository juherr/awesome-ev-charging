"""Row builders and stubs shared by the tests of the CSMS catalogue.

Not a test module and not a conftest: pytest neither collects nor
auto-loads it, so each test file imports what it uses instead of
importing from another, collected, test module.
"""

import csms


def cert(company="Acme Ltd", product="Acme CSMS", type_="Core + S",
         version="OCPP 2.0.1", software="1.0", number="OCA.1", url="https://oca/1.pdf",
         link="https://oca/acme", country="France", date="2024-01-01"):
  """One row shaped like csms-certificates.csv, every column present."""
  row = {field: "" for field in csms.CERT_FIELDS}
  row.update(certificate_no=number, company=company, company_link=link,
             country=country, product_designation=product, certificate_type=type_,
             software_version=software, protocol_version=version,
             date_of_registration=date, certificate_url=url,
             product_type=csms.OCA_PRODUCT_TYPE)
  return row


def vendor(**overrides):
  """One row shaped like csms.csv, every column present and empty by default."""
  row = {field: "" for field in csms.VENDOR_FIELDS}
  row.update(overrides)
  return row


def stub_github(monkeypatch, **repo_fields):
  """Answer enrich_from_github's only call without touching the network."""
  monkeypatch.setattr(csms.pipeline, "get_repo_data",
                      lambda repo, headers: {"html_url": f"https://github.com/{repo}",
                                             **repo_fields})
