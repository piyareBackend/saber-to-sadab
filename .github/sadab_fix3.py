from pathlib import Path

p = Path('test/nc_upload_download_test.dart')
t = p.read_text()
t = t.replace('    }.timeout(const Duration(seconds: 45)),\n    skip:', '    },\n    timeout: Timeout(const Duration(seconds: 45)),\n    skip:', 1)
p.write_text(t)

p = Path('lib/components/canvas/_canvas_painter.dart')
t = p.read_text().replace("import 'package:sadab/data/prefs.dart';\n", '')
p.write_text(t)
