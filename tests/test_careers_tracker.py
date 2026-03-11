from src.services.careers_tracker import CareerJob, build_summary, extract_jobs_from_html, short_market_note, snapshot_from_jobs, summarize_snapshot


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
    assert "Role trend:" in out
    assert "Takeaway: use this as Binance ecosystem / company-priority context" in out


def test_build_summary_and_short_note():
    jobs = [
        CareerJob(title="Security Engineer", team="Security", location="Remote"),
        CareerJob(title="Security Analyst", team="Security", location="Singapore"),
        CareerJob(title="Product Manager", team="Product", location="Singapore"),
    ]
    summary = build_summary(jobs)
    assert summary["openings"] == 3
    assert summary["top_teams"][0]["name"] == "Security"
    snapshot = snapshot_from_jobs(jobs, source="cache")
    note = short_market_note(snapshot)
    assert "Binance hiring pulse" in note
    assert "Treat this as ecosystem context" in note
