from src.services.careers_tracker import CareerJob, extract_jobs_from_html, snapshot_from_jobs, summarize_snapshot


def test_extract_jobs_from_jsonld_html():
    html = '''
    <html><head>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "JobPosting",
      "title": "Senior Product Manager, Wallet",
      "url": "https://example.com/jobs/1",
      "jobLocation": {
        "@type": "Place",
        "address": {
          "addressLocality": "Singapore",
          "addressCountry": "SG"
        }
      }
    }
    </script>
    </head></html>
    '''
    jobs = extract_jobs_from_html(html)
    assert len(jobs) == 1
    assert jobs[0].title == "Senior Product Manager, Wallet"
    assert "Singapore" in jobs[0].location


def test_summarize_snapshot_contains_takeaway():
    snapshot = snapshot_from_jobs(
        [
            CareerJob(title="Security Engineer", team="Security", location="Remote"),
            CareerJob(title="Product Manager", team="Product", location="Singapore"),
        ],
        source="cache",
    )
    out = summarize_snapshot(snapshot, limit=2)
    assert "Binance Careers Pulse" in out
    assert "Openings captured: 2" in out
    assert "Takeaway: use this as Binance ecosystem / company-priority context" in out
