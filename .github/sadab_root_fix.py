from pathlib import Path
import re

ROOT = Path('.')

def replace_once(path, old, new):
    p = ROOT / path
    text = p.read_text()
    if old not in text:
        raise SystemExit(f'pattern not found: {path}: {old[:100]!r}')
    p.write_text(text.replace(old, new, 1))

def write(path, text):
    (ROOT / path).write_text(text)

# Nextcloud integration is opt-in and bounded.
p = ROOT / 'test/nc_upload_download_test.dart'
t = p.read_text()
t = t.replace('    retry: 2,\n', '')
if 'timeout(const Duration(seconds: 45))' not in t:
    t = t.replace('    },\n    skip: hasIntegrationConfig', '    }.timeout(const Duration(seconds: 45)),\n    skip: hasIntegrationConfig', 1)
p.write_text(t)

# Floating toolbox must be a Stack overlay; palm rejection is inverse of finger drawing.
p = ROOT / 'lib/pages/editor/editor.dart'
t = p.read_text()
old = """  void sadabShowShapes() {\n    showDialog(\n      context: context,\n      builder: (_) => ShapePaletteDialog(\n        onSelected: (_) => setState(() => currentTool = ShapePen()),\n      ),\n    );\n  }"""
new = """  void sadabShowShapes() {\n    showDialog(\n      context: context,\n      builder: (_) => ShapePaletteDialog(\n        onSelected: (definition) => setState(() {\n          ShapePen.selectedDefinition = definition;\n          currentTool = ShapePen(definition: definition);\n        }),\n      ),\n    );\n  }"""
if old not in t: raise SystemExit('shape dialog block missing')
t = t.replace(old, new, 1)
old = """        body: body,\n        floatingActionButton: FloatingToolbox(\n          onPenPreset: sadabPenPreset,\n          onEraser: () => setState(() => currentTool = Eraser()),\n          onUndo: undo,\n          onRedo: redo,\n          onPalmRejection: (v) =>\n              setState(() => stows.editorFingerDrawing.value = v),\n          onShapes: sadabShowShapes,\n        ),\n"""
new = """        body: Stack(\n          children: [\n            Positioned.fill(child: body),\n            FloatingToolbox(\n              onPenPreset: sadabPenPreset,\n              onEraser: () => setState(() => currentTool = Eraser()),\n              onUndo: undo,\n              onRedo: redo,\n              onPalmRejection: (enabled) => setState(() {\n                stows.editorFingerDrawing.value = !enabled;\n                lastSeenPointerCount = 0;\n              }),\n              onShapes: sadabShowShapes,\n            ),\n          ],\n        ),\n"""
if old not in t: raise SystemExit('floating toolbox block missing')
p.write_text(t.replace(old, new, 1))

write('lib/components/toolbar/floating_toolbox.dart', '''import 'package:flutter/material.dart';

class FloatingToolbox extends StatefulWidget {
  const new({super.key, required this.onPenPreset, required this.onEraser, required this.onUndo, required this.onRedo, required this.onPalmRejection, required this.onShapes});
  final ValueChanged<int> onPenPreset;
  final VoidCallback onEraser;
  final VoidCallback onUndo;
  final VoidCallback onRedo;
  final ValueChanged<bool> onPalmRejection;
  final VoidCallback onShapes;

  @override
  State<FloatingToolbox> createState() => _FloatingToolboxState();
}

class _FloatingToolboxState extends State<FloatingToolbox> {
  var position = const Offset(24, 180);
  var palmRejection = true;

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.sizeOf(context);
    const width = 330.0;
    const height = 72.0;
    final maxX = (size.width - width - 8).clamp(8.0, double.infinity);
    final maxY = (size.height - height - 8).clamp(8.0, double.infinity);
    final safe = Offset(position.dx.clamp(8.0, maxX), position.dy.clamp(8.0, maxY));
    if (safe != position) {
      WidgetsBinding.instance.addPostFrameCallback((_) { if (mounted) setState(() => position = safe); });
    }
    return Positioned(
      left: safe.dx,
      top: safe.dy,
      child: Material(
        elevation: 8,
        color: Theme.of(context).colorScheme.surface.withValues(alpha: .94),
        shape: const StadiumBorder(),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
          child: GestureDetector(
            behavior: HitTestBehavior.opaque,
            onPanUpdate: (d) => setState(() => position = Offset((position.dx + d.delta.dx).clamp(8.0, maxX), (position.dy + d.delta.dy).clamp(8.0, maxY))),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                ...[1, 2, 3].map((i) => _b('P$i', () => widget.onPenPreset(i))),
                _b('E', widget.onEraser), _b('↶', widget.onUndo), _b('↷', widget.onRedo), _b('◇', widget.onShapes),
                IconButton(
                  tooltip: palmRejection ? 'Palm rejection on' : 'Palm rejection off',
                  isSelected: palmRejection,
                  onPressed: () { final next = !palmRejection; setState(() => palmRejection = next); widget.onPalmRejection(next); },
                  icon: const Icon(Icons.back_hand_outlined),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _b(String text, VoidCallback onPressed) => Padding(
    padding: const EdgeInsets.symmetric(horizontal: 2),
    child: IconButton.filledTonal(onPressed: onPressed, icon: Text(text, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12))),
  );
}
''')

# Shape definition is UI/tool state only. Storage and sync models remain untouched.
p = ROOT / 'lib/data/tools/shape_pen.dart'
t = p.read_text()
if "components/shapes/custom_shape_engine.dart" not in t:
    t = t.replace("import 'package:sadab/components/canvas/_stroke.dart';\n", "import 'package:sadab/components/canvas/_stroke.dart';\nimport 'package:sadab/components/shapes/custom_shape_engine.dart';\n", 1)
t = t.replace('class ShapePen extends Pen {\n  new()\n', 'class ShapePen extends Pen {\n  ShapePen({CustomShapeDefinition? definition})\n    : definition = definition ?? selectedDefinition,\n', 1)
if 'final CustomShapeDefinition definition;' not in t:
    t = t.replace('        toolId: .shapePen,\n      );\n', '        toolId: .shapePen,\n      );\n\n  final CustomShapeDefinition definition;\n  static CustomShapeDefinition selectedDefinition = CustomShapeRegistry.defaults.first;\n  static final Map<Stroke, CustomShapeDefinition> definitionsByStroke = {};\n', 1)
t = t.replace('    if (rawStroke == null) return null;\n    assert(rawStroke.options.isComplete == true);', '    if (rawStroke == null) return null;\n    assert(rawStroke.options.isComplete == true);\n    definitionsByStroke[rawStroke] = definition;', 1)
p.write_text(t)

# Full shape renderer for all advertised shapes/styles.
write('lib/components/shapes/custom_shape_engine.dart', '''import 'dart:math' as math;
import 'package:flutter/material.dart';

enum ShapeKind { line, arrow, doubleArrow, rectangle, roundedRect, ellipse, axes, triangle, star }
enum ShapeFill { transparent, translucent, solid }
enum ShapeStrokeStyle { solid, dotted, dashed }

class CustomShapeDefinition {
  const new({required this.id, required this.label, required this.kind, this.fill = ShapeFill.transparent, this.strokeStyle = ShapeStrokeStyle.solid, this.lineWeight = 3});
  final String id;
  final String label;
  final ShapeKind kind;
  final ShapeFill fill;
  final ShapeStrokeStyle strokeStyle;
  final double lineWeight;
}

class CustomShapeRegistry {
  static const defaults = <CustomShapeDefinition>[
    CustomShapeDefinition(id: 'line', label: 'Line', kind: ShapeKind.line),
    CustomShapeDefinition(id: 'arrow', label: 'Arrow', kind: ShapeKind.arrow),
    CustomShapeDefinition(id: 'double-arrow', label: 'Double Arrow', kind: ShapeKind.doubleArrow),
    CustomShapeDefinition(id: 'rectangle', label: 'Rectangle', kind: ShapeKind.rectangle),
    CustomShapeDefinition(id: 'rounded-rect', label: 'Rounded Rect', kind: ShapeKind.roundedRect),
    CustomShapeDefinition(id: 'ellipse', label: 'Circle / Ellipse', kind: ShapeKind.ellipse),
    CustomShapeDefinition(id: 'axes', label: 'Coordinate Axes', kind: ShapeKind.axes),
    CustomShapeDefinition(id: 'triangle', label: 'Triangle', kind: ShapeKind.triangle),
    CustomShapeDefinition(id: 'star', label: 'Star', kind: ShapeKind.star),
  ];
  final List<CustomShapeDefinition> custom = [];
  List<CustomShapeDefinition> get all => [...defaults, ...custom];
  void add(CustomShapeDefinition definition) => custom.add(definition);
}

class ShapeSnapAssist {
  static double snapAngle(double radians, {double increment = math.pi / 12}) => (radians / increment).round() * increment;
  static Rect normalizeRect(Offset a, Offset b) => Rect.fromPoints(a, b);
}

class CustomShapeRenderer {
  static void draw(Canvas canvas, List<Offset> points, CustomShapeDefinition definition, Color color) {
    if (points.length < 2) return;
    final r = _bounds(points);
    final paint = Paint()
      ..color = color
      ..strokeWidth = definition.lineWeight.clamp(1, 25)
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    final path = _path(definition.kind, r);
    if (definition.fill != ShapeFill.transparent && _isClosed(definition.kind)) {
      canvas.drawPath(path, paint..style = PaintingStyle.fill..color = color.withValues(alpha: definition.fill == ShapeFill.solid ? .95 : .28));
    }
    if (definition.strokeStyle == ShapeStrokeStyle.solid) {
      canvas.drawPath(path, paint..style = PaintingStyle.stroke..color = color);
    } else if (definition.strokeStyle == ShapeStrokeStyle.dashed) {
      _dash(canvas, path, paint..style = PaintingStyle.stroke..color = color);
    } else {
      _dot(canvas, path, paint..style = PaintingStyle.fill..color = color);
    }
  }

  static Rect _bounds(List<Offset> points) {
    var l = points.first.dx, t = points.first.dy, r = l, b = t;
    for (final p in points.skip(1)) { l = math.min(l, p.dx); t = math.min(t, p.dy); r = math.max(r, p.dx); b = math.max(b, p.dy); }
    return Rect.fromLTRB(l, t, r, b);
  }

  static bool _isClosed(ShapeKind k) => k == ShapeKind.rectangle || k == ShapeKind.roundedRect || k == ShapeKind.ellipse || k == ShapeKind.triangle || k == ShapeKind.star;

  static Path _path(ShapeKind k, Rect r) {
    final p = Path(); final c = r.center;
    switch (k) {
      case ShapeKind.line: p.moveTo(r.left, c.dy); p.lineTo(r.right, c.dy);
      case ShapeKind.arrow: _arrowLine(p, Offset(r.left, c.dy), Offset(r.right, c.dy));
      case ShapeKind.doubleArrow: _arrowLine(p, Offset(r.left, c.dy), Offset(r.right, c.dy)); _head(p, Offset(r.left, c.dy), const Offset(1, 0));
      case ShapeKind.rectangle: p.addRect(r);
      case ShapeKind.roundedRect: p.addRRect(RRect.fromRectAndRadius(r, Radius.circular(math.min(r.shortestSide * .2, 28))));
      case ShapeKind.ellipse: p.addOval(r);
      case ShapeKind.axes:
        p.moveTo(r.left, c.dy); p.lineTo(r.right, c.dy); p.moveTo(c.dx, r.bottom); p.lineTo(c.dx, r.top); _head(p, Offset(r.right, c.dy), const Offset(-1, 0)); _head(p, Offset(c.dx, r.top), const Offset(0, 1));
      case ShapeKind.triangle: p.moveTo(c.dx, r.top); p.lineTo(r.right, r.bottom); p.lineTo(r.left, r.bottom); p.close();
      case ShapeKind.star:
        for (var i = 0; i < 10; i++) { final a = -math.pi / 2 + i * math.pi / 5; final rr = i.isEven ? r.shortestSide / 2 : r.shortestSide * .21; final q = Offset(c.dx + math.cos(a) * rr, c.dy + math.sin(a) * rr); if (i == 0) p.moveTo(q.dx, q.dy); else p.lineTo(q.dx, q.dy); } p.close();
    }
    return p;
  }

  static void _arrowLine(Path p, Offset a, Offset b) { p.moveTo(a.dx, a.dy); p.lineTo(b.dx, b.dy); _head(p, b, Offset(a.dx - b.dx, a.dy - b.dy)); }
  static void _head(Path p, Offset tip, Offset dir) { final d = dir.distance; if (d == 0) return; final u = dir / d; final s = Offset(-u.dy, u.dx); final base = tip + u * 14; p.moveTo(tip.dx, tip.dy); p.lineTo((base + s * 7).dx, (base + s * 7).dy); p.moveTo(tip.dx, tip.dy); p.lineTo((base - s * 7).dx, (base - s * 7).dy); }
  static void _dash(Canvas c, Path path, Paint paint) { for (final m in path.computeMetrics()) { for (double d = 0; d < m.length; d += 16) { c.drawPath(m.extractPath(d, math.min(d + 9, m.length)), paint); } } }
  static void _dot(Canvas c, Path path, Paint paint) { for (final m in path.computeMetrics()) { for (double d = 0; d < m.length; d += 11) { final x = m.getTangentForOffset(d); if (x != null) c.drawCircle(x.position, paint.strokeWidth / 2, paint); } } }
}
''')

# Integrate the shape renderer into the existing painter without changing stroke serialization.
p = ROOT / 'lib/components/canvas/_canvas_painter.dart'
t = p.read_text()
if "components/shapes/custom_shape_engine.dart" not in t:
    t = t.replace("import 'package:sadab/components/canvas/_stroke.dart';", "import 'package:sadab/components/canvas/_stroke.dart';\nimport 'package:sadab/components/shapes/custom_shape_engine.dart';", 1)
needle = """    for (final stroke in strokes) {\n      if (stroke.toolId == .highlighter) continue;\n\n      var color = stroke.color.withInversion(invert);\n"""
repl = """    for (final stroke in strokes) {\n      if (stroke.toolId == .highlighter) continue;\n\n      var color = stroke.color.withInversion(invert);\n      if (stroke.toolId == .shapePen) {\n        final definition = ShapePen.definitionsByStroke[stroke] ?? ShapePen.selectedDefinition;\n        CustomShapeRenderer.draw(canvas, stroke.lowQualityPolygon, definition, color);\n        continue;\n      }\n"""
if needle in t: t = t.replace(needle, repl, 1)
needle = """    final color = currentStroke!.color.withInversion(invert);\n    final paint = Paint();\n"""
repl = """    final color = currentStroke!.color.withInversion(invert);\n    if (currentStroke!.toolId == .shapePen) {\n      final definition = ShapePen.definitionsByStroke[currentStroke!] ?? ShapePen.selectedDefinition;\n      CustomShapeRenderer.draw(canvas, currentStroke!.lowQualityPolygon, definition, color);\n      return;\n    }\n    final paint = Paint();\n"""
if needle in t: t = t.replace(needle, repl, 1)
# High contrast follows explicit paper brightness.
if "package:sadab/data/prefs.dart" not in t:
    t = t.replace("import 'package:sadab/data/tools/shape_pen.dart';", "import 'package:sadab/data/tools/shape_pen.dart';\nimport 'package:sadab/data/prefs.dart';", 1)
t = t.replace("      var color = stroke.color.withInversion(invert);\n", "      var color = stroke.color.withInversion(invert);\n", 1)
p.write_text(t)

# Reactive paper controls and dark-paper contrast.
p = ROOT / 'lib/components/canvas/inner_canvas.dart'
t = p.read_text()
if 'AnimatedBuilder(' not in t:
    t = t.replace('  Widget build(BuildContext context) {\n    final theme = Theme.of(context);', '  Widget build(BuildContext context) {\n    return AnimatedBuilder(\n      animation: Listenable.merge([stows.sadabEInkMode, stows.sadabPaperPreset, stows.sadabHighContrastInk]),\n      builder: (context, _) => _buildCanvas(context),\n    );\n  }\n\n  Widget _buildCanvas(BuildContext context) {\n    final theme = Theme.of(context);', 1)
p.write_text(t)

p = ROOT / 'lib/components/canvas/canvas.dart'
t = p.read_text()
if 'AnimatedBuilder(' not in t:
    t = t.replace('  Widget build(BuildContext context) {\n    return Center(', '  Widget build(BuildContext context) {\n    return AnimatedBuilder(\n      animation: Listenable.merge([stows.sadabEInkMode, stows.sadabPaperPreset, stows.sadabHighContrastInk]),\n      builder: (context, _) => Center(', 1)
    idx = t.rfind('    );\n  }\n}')
    if idx != -1: t = t[:idx] + '      ),\n    );\n  }\n}' + t[idx+len('    );\n  }\n}'):]
dark = """    if (stows.sadabHighContrastInk.value) return Colors.black;"""
t = t.replace(dark, """    if (stows.sadabHighContrastInk.value) {\n      return darkPaper ? Colors.white : Colors.black;\n    }""", 1)
t = t.replace("    if (currentTool is Pen) return (currentTool as Pen).color;\n    return Colors.black;", "    if (currentTool is Pen) return (currentTool as Pen).color;\n    return darkPaper ? Colors.white : Colors.black;", 1)
# Inject darkPaper before contrast check.
t = t.replace('  Color _getOnyxColor() {\n', "  Color _getOnyxColor() {\n    final darkPaper = stows.sadabEInkMode.value && stows.sadabPaperPreset.value == SadabPaperPreset.mutedNight;\n", 1)
p.write_text(t)

# Remove every stale package import.
for p in ROOT.rglob('*.dart'):
    s = p.read_text(errors='ignore')
    u = s.replace('package:saber/', 'package:sadab/')
    if u != s: p.write_text(u)

# CI command normalization + Android build.
p = ROOT / '.github/workflows/tests.yml'
t = p.read_text()
t = t.replace('dart format lib packages scripts test --output none --set-exit-if-changed', 'dart format --set-exit-if-changed .')
if 'name: Build Android debug APK' not in t:
    t += '\n      - name: Build Android debug APK\n        working-directory: android\n        run: ./gradlew assembleDebug\n'
p.write_text(t)

print('Sadab root fixes staged in working tree.')
