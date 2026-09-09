from pathlib import Path
import re

# ShapePen constructor repair: the previous transform must preserve Pen's super initializer.
p = Path('lib/data/tools/shape_pen.dart')
t = p.read_text()
if "components/shapes/custom_shape_engine.dart" not in t:
    t = t.replace("import 'package:sadab/components/canvas/_stroke.dart';\n", "import 'package:sadab/components/canvas/_stroke.dart';\nimport 'package:sadab/components/shapes/custom_shape_engine.dart';\n", 1)
t = t.replace("class ShapePen extends Pen {\n  new()\n    : super(", "class ShapePen extends Pen {\n  ShapePen({CustomShapeDefinition? definition})\n    : definition = definition ?? selectedDefinition,\n      super(", 1)
if 'final CustomShapeDefinition definition;' not in t:
    marker = "        toolId: .shapePen,\n      );\n"
    t = t.replace(marker, marker + "\n  final CustomShapeDefinition definition;\n  static CustomShapeDefinition selectedDefinition = CustomShapeRegistry.defaults.first;\n  static final Map<Stroke, CustomShapeDefinition> definitionsByStroke = {};\n", 1)
if 'definitionsByStroke[rawStroke]' not in t:
    t = t.replace("    if (rawStroke == null) return null;\n    assert(rawStroke.options.isComplete == true);", "    if (rawStroke == null) return null;\n    assert(rawStroke.options.isComplete == true);\n    definitionsByStroke[rawStroke] = definition;", 1)
p.write_text(t)

# Bound the external Nextcloud test without changing its opt-in semantics.
p = Path('test/nc_upload_download_test.dart')
t = p.read_text()
t = t.replace('    },\n    skip: hasIntegrationConfig', '    }.timeout(const Duration(seconds: 45)),\n    skip: hasIntegrationConfig', 1)
t = t.replace('    retry: 2,\n', '', 1)
p.write_text(t)

# Deterministic image precaching in sbn_test: Future.wait must receive Futures only.
p = Path('test/sbn_test.dart')
t = p.read_text()
old = '''  await Future.wait([\n    for (final image in page.images)\n      if (image is PngEditorImage)\n        if (image.imageProvider is FileImage)\n          (image.imageProvider as FileImage).file.readAsBytes().then(\n            (bytes) => image.imageProvider = MemoryImage(bytes),\n          ),\n    if (backgroundImage is PngEditorImage)\n      if (backgroundImage.imageProvider is FileImage)\n        (backgroundImage.imageProvider as PngEditorImage).imageProvider =\n            MemoryImage(\n              await (backgroundImage.imageProvider as FileImage).file\n                  .readAsBytes(),\n            ),\n  ]);'''
new = '''  final precacheFutures = <Future<void>>[];\n  for (final image in page.images) {\n    if (image is PngEditorImage && image.imageProvider is FileImage) {\n      final file = (image.imageProvider as FileImage).file;\n      precacheFutures.add(file.readAsBytes().then((bytes) {\n        image.imageProvider = MemoryImage(bytes);\n      }));\n    }\n  }\n  if (backgroundImage is PngEditorImage &&\n      backgroundImage.imageProvider is FileImage) {\n    final file = (backgroundImage.imageProvider as FileImage).file;\n    precacheFutures.add(file.readAsBytes().then((bytes) {\n      backgroundImage.imageProvider = MemoryImage(bytes);\n    }));\n  }\n  await Future.wait(precacheFutures);'''
if old not in t:
    raise SystemExit('sbn precache block not found')
t = t.replace(old, new, 1)
p.write_text(t)

# Remove now-unused prefs import from painter if present.
p = Path('lib/components/canvas/_canvas_painter.dart')
t = p.read_text().replace("import 'package:sadab/data/prefs.dart';\n", '')
p.write_text(t)
