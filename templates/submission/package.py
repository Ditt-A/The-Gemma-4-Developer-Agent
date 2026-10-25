archive_path = OUTPUT / 'submission.zip'
with zipfile.ZipFile(archive_path, 'w') as archive:
    for name, content in sorted(FILES.items()):
        info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
        info.create_system = 3
        info.external_attr = 0o100644 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, content.encode('utf-8'))
with zipfile.ZipFile(archive_path) as archive:
    assert archive.testzip() is None
    assert set(archive.namelist()) == set(FILES)
    for name, content in FILES.items():
        assert archive.read(name) == content.encode('utf-8')
receipt = {
    'candidate': CANDIDATE_ID,
    'archive_sha256': hashlib.sha256(archive_path.read_bytes()).hexdigest(),
    'archive_bytes': archive_path.stat().st_size,
    'members': {n: hashlib.sha256(v.encode('utf-8')).hexdigest() for n,v in FILES.items()},
    'packaging_checks_passed': True,
    'leaderboard_score': None,
    'model_quality_measured_by_this_notebook': False,
}
(OUTPUT / 'build_receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps(receipt, indent=2))
print('Ready:', archive_path)
