from pathlib import Path
import re

root = Path('.')

def edit(path, transform):
    p = root / path
    text = p.read_text()
    new = transform(text)
    if text == new:
        raise RuntimeError(f'No change produced for {path}')
    p.write_text(new)

# Branding: update application/package identity while preserving storage and network compatibility keys.
edit('pubspec.yaml', lambda s: s.replace('name: saber\n', 'name: sadab\n', 1).replace('description: A cross-platform libre notes app', 'description: A distraction-free study and reading app', 1))
edit('lib/main.dart', lambda s: s.replace("title: 'Saber'", "title: 'Sadab'", 1).replace('package:saber/', 'package:sadab/'))

# Internal Dart imports follow the package rename.
for p in (root / 'lib').rglob('*.dart'):
    s = p.read_text()
    n = s.replace('package:saber/', 'package:sadab/')
    if n != s:
        p.write_text(n)

# Paper comfort preferences.
prefs = root / 'lib/data/prefs.dart'
s = prefs.read_text()
if 'enum SadabPaperPreset' not in s:
    marker = 'var _isOnMainIsolate = false;\n'
    addition = '''\nenum SadabPaperPreset { warmPaper, eInkNeutral, mutedNight }\n\nColor sadabPaperColor(SadabPaperPreset preset) => switch (preset) {\n  SadabPaperPreset.warmPaper => const Color(0xFFF4ECD8),\n  SadabPaperPreset.eInkNeutral => const Color(0xFFE5E0D8),\n  SadabPaperPreset.mutedNight => const Color(0xFF1A1A1A),\n};\n'''
    s = s.replace(marker, marker + addition, 1)
block = """  final sadabEInkMode = PlainStow('sadabEInkMode', false, volatile: !_isOnMainIsolate);\n  final sadabHighContrastInk = PlainStow('sadabHighContrastInk', false, volatile: !_isOnMainIsolate);\n  final sadabPaperPreset = PlainStow(\n    'sadabPaperPreset', SadabPaperPreset.eInkNeutral,\n    codec: const EnumCodec(SadabPaperPreset.values), volatile: !_isOnMainIsolate,\n  );\n\n"""
if 'final sadabEInkMode' not in s:
    s = s.replace('  final customDataDir = PlainStow<String?>(', block + '  final customDataDir = PlainStow<String?>(', 1)
prefs.write_text(s)

# Existing Onyx wrapper remains untouched; only the color supplied to it changes.
edit('lib/components/canvas/canvas.dart', lambda s: s
     .replace("import 'package:sadab/data/tools/select.dart';\n", "import 'package:sadab/data/tools/select.dart';\nimport 'package:sadab/data/prefs.dart';\n", 1)
     .replace("import 'package:saber/data/tools/select.dart';\n", "import 'package:sadab/data/tools/select.dart';\nimport 'package:sadab/data/prefs.dart';\n", 1)
     .replace('  Color _getOnyxColor() {\n    if (currentTool is Pen) {', '  Color _getOnyxColor() {\n    if (stows.sadabHighContrastInk.value) return Colors.black;\n    if (currentTool is Pen) {', 1)
)

# Paper presentation layer and inversion guard.
inner = root / 'lib/components/canvas/inner_canvas.dart'
s = inner.read_text()
if 'package:sadab/components/canvas/paper_grain.dart' not in s:
    s = s.replace("import 'package:saber/components/canvas/image/editor_image.dart';\n", "import 'package:saber/components/canvas/image/editor_image.dart';\nimport 'package:saber/components/canvas/paper_grain.dart';\nimport 'package:saber/data/prefs.dart';\n", 1)
    s = s.replace('package:saber/', 'package:sadab/')
s = s.replace('final invert = stows.editorAutoInvert.value && brightness == .dark;', 'final invert = stows.editorAutoInvert.value && brightness == .dark && !stows.sadabEInkMode.value;', 1)
s = s.replace('final Color backgroundColor = widget.coreInfo.backgroundColor ?? InnerCanvas.defaultBackgroundColor;', 'final Color backgroundColor = stows.sadabEInkMode.value ? sadabPaperColor(stows.sadabPaperPreset.value) : (widget.coreInfo.backgroundColor ?? InnerCanvas.defaultBackgroundColor);', 1)
if 'const Positioned.fill(child: PaperGrain())' not in s:
    s = s.replace('        if (page.backgroundImage == null)\n', '        if (stows.sadabEInkMode.value && page.backgroundImage == null)\n          const Positioned.fill(child: PaperGrain()),\n        if (page.backgroundImage == null)\n', 1)
inner.write_text(s)

# Compact toolbar button ergonomics.
edit('lib/components/toolbar/toolbar_button.dart', lambda s: s
     .replace('package:saber/', 'package:sadab/')
     .replace('return IconButton(', 'return IconButton.filled(', 1)
     .replace('        icon: icon,', '        icon: icon,\n        style: IconButton.styleFrom(minimumSize: const Size(38, 38), maximumSize: const Size(42, 42), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)), padding: const EdgeInsets.all(8)),', 1)
)

# New, cache-friendly paper grain renderer.
(root / 'lib/components/canvas/grayscale_widget.dart').write_text('''import \'package:flutter/material.dart\';\n\nclass GrayscaleWidget extends StatelessWidget {\n  const GrayscaleWidget({super.key, required this.child});\n  final Widget child;\n\n  static const ColorFilter filter = ColorFilter.matrix(<double>[\n    0.2126, 0.7152, 0.0722, 0, 0,\n    0.2126, 0.7152, 0.0722, 0, 0,\n    0.2126, 0.7152, 0.0722, 0, 0,\n    0, 0, 0, 1, 0,\n  ]);\n\n  @override\n  Widget build(BuildContext context) => ColorFiltered(colorFilter: filter, child: child);\n}\n''')
(root / 'lib/components/canvas/paper_grain.dart').write_text('''import \'package:flutter/material.dart\';\n\nclass PaperGrainPainter extends CustomPainter {\n  const PaperGrainPainter();\n  static final List<Offset> _points = List<Offset>.generate(420, (i) {\n    final x = ((i * 73) % 997) / 997.0;\n    final y = ((i * 181 + 31) % 991) / 991.0;\n    return Offset(x, y);\n  }, growable: false);\n\n  @override\n  void paint(Canvas canvas, Size size) {\n    final paint = Paint()..color = Colors.black.withValues(alpha: 0.022);\n    for (final point in _points) {\n      canvas.drawCircle(Offset(point.dx * size.width, point.dy * size.height), 0.45, paint);\n    }\n  }\n\n  @override\n  bool shouldRepaint(covariant PaperGrainPainter oldDelegate) => false;\n}\n\nclass PaperGrain extends StatelessWidget {\n  const PaperGrain({super.key});\n  @override\n  Widget build(BuildContext context) => const IgnorePointer(child: RepaintBoundary(child: CustomPaint(painter: PaperGrainPainter())));\n}\n''')

(root / 'lib/components/shapes/custom_shape_engine.dart').write_text('''import \'dart:math\' as math;\nimport \'package:flutter/material.dart\';\n\nenum ShapeKind { line, arrow, doubleArrow, rectangle, roundedRect, ellipse, axes, triangle, star }\nenum ShapeFill { transparent, translucent, solid }\nenum ShapeStrokeStyle { solid, dotted, dashed }\n\nclass CustomShapeDefinition {\n  const CustomShapeDefinition({required this.id, required this.label, required this.kind, this.fill = ShapeFill.transparent, this.strokeStyle = ShapeStrokeStyle.solid, this.lineWeight = 3});\n  final String id; final String label; final ShapeKind kind;\n  final ShapeFill fill; final ShapeStrokeStyle strokeStyle; final double lineWeight;\n}\n\nclass CustomShapeRegistry {\n  static const defaults = <CustomShapeDefinition>[\n    CustomShapeDefinition(id: \'line\', label: \'Line\', kind: ShapeKind.line),\n    CustomShapeDefinition(id: \'arrow\', label: \'Arrow\', kind: ShapeKind.arrow),\n    CustomShapeDefinition(id: \'double-arrow\', label: \'Double Arrow\', kind: ShapeKind.doubleArrow),\n    CustomShapeDefinition(id: \'rectangle\', label: \'Rectangle\', kind: ShapeKind.rectangle),\n    CustomShapeDefinition(id: \'rounded-rect\', label: \'Rounded Rect\', kind: ShapeKind.roundedRect),\n    CustomShapeDefinition(id: \'ellipse\', label: \'Circle / Ellipse\', kind: ShapeKind.ellipse),\n    CustomShapeDefinition(id: \'axes\', label: \'Coordinate Axes\', kind: ShapeKind.axes),\n    CustomShapeDefinition(id: \'triangle\', label: \'Triangle\', kind: ShapeKind.triangle),\n    CustomShapeDefinition(id: \'star\', label: \'Star\', kind: ShapeKind.star),\n  ];\n  final List<CustomShapeDefinition> custom = [];\n  List<CustomShapeDefinition> get all => [...defaults, ...custom];\n  void add(CustomShapeDefinition definition) => custom.add(definition);\n}\n\nclass ShapeSnapAssist {\n  static double snapAngle(double radians, {double increment = math.pi / 12}) => (radians / increment).round() * increment;\n  static Rect normalizeRect(Offset a, Offset b) => Rect.fromPoints(a, b);\n}\n''')
(root / 'lib/components/shapes/shape_palette_dialog.dart').write_text('''import \'package:flutter/material.dart\';\nimport \'package:sadab/components/shapes/custom_shape_engine.dart\';\n\nclass ShapePaletteDialog extends StatefulWidget {\n  const ShapePaletteDialog({super.key, required this.onSelected});\n  final ValueChanged<CustomShapeDefinition> onSelected;\n  @override State<ShapePaletteDialog> createState() => _ShapePaletteDialogState();\n}\n\nclass _ShapePaletteDialogState extends State<ShapePaletteDialog> {\n  ShapeFill fill = ShapeFill.transparent; ShapeStrokeStyle stroke = ShapeStrokeStyle.solid; double weight = 3;\n  IconData iconFor(ShapeKind kind) => switch (kind) {\n    ShapeKind.line => Icons.horizontal_rule, ShapeKind.arrow => Icons.arrow_forward, ShapeKind.doubleArrow => Icons.swap_horiz,\n    ShapeKind.rectangle => Icons.crop_square, ShapeKind.roundedRect => Icons.rounded_corner, ShapeKind.ellipse => Icons.circle_outlined,\n    ShapeKind.axes => Icons.center_focus_strong, ShapeKind.triangle => Icons.change_history, ShapeKind.star => Icons.star_border,\n  };\n  @override\n  Widget build(BuildContext context) => AlertDialog(\n    title: const Text(\'Shapes\'),\n    content: SizedBox(width: 420, child: Column(mainAxisSize: MainAxisSize.min, children: [\n      GridView.builder(shrinkWrap: true, gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, crossAxisSpacing: 8, mainAxisSpacing: 8), itemCount: CustomShapeRegistry.defaults.length, itemBuilder: (_, i) {\n        final shape = CustomShapeRegistry.defaults[i];\n        return OutlinedButton(onPressed: () { widget.onSelected(CustomShapeDefinition(id: shape.id, label: shape.label, kind: shape.kind, fill: fill, strokeStyle: stroke, lineWeight: weight)); Navigator.pop(context); }, child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(iconFor(shape.kind)), Text(shape.label, textAlign: TextAlign.center, style: const TextStyle(fontSize: 11))]));\n      }),\n      const SizedBox(height: 12),\n      SegmentedButton<ShapeFill>(segments: const [ButtonSegment(value: ShapeFill.transparent, label: Text(\'Clear\')), ButtonSegment(value: ShapeFill.translucent, label: Text(\'Glass\')), ButtonSegment(value: ShapeFill.solid, label: Text(\'Solid\'))], selected: {fill}, onSelectionChanged: (v) => setState(() => fill = v.first)),\n      SegmentedButton<ShapeStrokeStyle>(segments: const [ButtonSegment(value: ShapeStrokeStyle.solid, label: Text(\'Solid\')), ButtonSegment(value: ShapeStrokeStyle.dotted, label: Text(\'Dotted\')), ButtonSegment(value: ShapeStrokeStyle.dashed, label: Text(\'Dashed\'))], selected: {stroke}, onSelectionChanged: (v) => setState(() => stroke = v.first)),\n      Row(children: [const Text(\'Weight\'), Expanded(child: Slider(min: 1, max: 12, divisions: 11, value: weight, onChanged: (v) => setState(() => weight = v)))])\n    ])),\n  );\n}\n''')
(root / 'lib/components/toolbar/floating_toolbox.dart').write_text('''import \'package:flutter/material.dart\';\n\nclass FloatingToolbox extends StatefulWidget {\n  const FloatingToolbox({super.key, required this.onPenPreset, required this.onEraser, required this.onUndo, required this.onRedo, required this.onPalmRejection, required this.onShapes});\n  final ValueChanged<int> onPenPreset; final VoidCallback onEraser; final VoidCallback onUndo; final VoidCallback onRedo;\n  final ValueChanged<bool> onPalmRejection; final VoidCallback onShapes;\n  @override State<FloatingToolbox> createState() => _FloatingToolboxState();\n}\nclass _FloatingToolboxState extends State<FloatingToolbox> {\n  Offset position = const Offset(24, 180); bool palm = true;\n  @override Widget build(BuildContext context) => LayoutBuilder(builder: (context, constraints) {\n    final maxX = (constraints.maxWidth - 320).clamp(8.0, double.infinity); final maxY = (constraints.maxHeight - 72).clamp(8.0, double.infinity);\n    position = Offset(position.dx.clamp(8.0, maxX), position.dy.clamp(8.0, maxY));\n    return Positioned(left: position.dx, top: position.dy, child: GestureDetector(onPanUpdate: (d) => setState(() => position += d.delta), child: Material(elevation: 8, color: Theme.of(context).colorScheme.surface.withValues(alpha: .94), shape: const StadiumBorder(), child: Padding(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6), child: Row(mainAxisSize: MainAxisSize.min, children: [\n      ...[1,2,3].map((i) => _b(\'P$i\', () => widget.onPenPreset(i))), _b(\'E\', widget.onEraser), _b(\'↶\', widget.onUndo), _b(\'↷\', widget.onRedo), _b(\'◇\', widget.onShapes),\n      IconButton(tooltip: \'Palm rejection\', isSelected: palm, onPressed: () { setState(() => palm = !palm); widget.onPalmRejection(palm); }, icon: const Icon(Icons.back_hand_outlined)),\n    ]))));\n  });\n  Widget _b(String text, VoidCallback onPressed) => Padding(padding: const EdgeInsets.symmetric(horizontal: 2), child: IconButton.filledTonal(onPressed: onPressed, icon: Text(text, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12))));\n}\n''')

# Add floating shape/tool access without rewriting the input pipeline.
ep = root / 'lib/pages/editor/editor.dart'
s = ep.read_text()
if 'floating_toolbox.dart' not in s:
    s = s.replace("import 'package:sadab/components/toolbar/toolbar.dart';\n", "import 'package:sadab/components/toolbar/toolbar.dart';\nimport 'package:sadab/components/toolbar/floating_toolbox.dart';\nimport 'package:sadab/components/shapes/shape_palette_dialog.dart';\n", 1)
helper = '''\n  void sadabShowShapes() {\n    showDialog(context: context, builder: (_) => ShapePaletteDialog(onSelected: (_) => setState(() => currentTool = ShapePen())));\n  }\n\n  void sadabPenPreset(int preset) {\n    setState(() { currentTool = switch (preset) { 1 => Pen.fountainPen(), 2 => Pen.ballpointPen(), _ => Pencil.currentPencil }; });\n  }\n'''
if 'void sadabShowShapes()' not in s:
    s = s.replace('  @override\n  Widget build(BuildContext context) {', helper + '\n  @override\n  Widget build(BuildContext context) {', 1)
if 'FloatingToolbox(onPenPreset:' not in s:
    s = s.replace('        floatingActionButton:\n', '        floatingActionButton: FloatingToolbox(onPenPreset: sadabPenPreset, onEraser: () => setState(() => currentTool = Eraser()), onUndo: undo, onRedo: redo, onPalmRejection: (v) => setState(() => stows.editorFingerDrawing.value = v), onShapes: sadabShowShapes),\n        /* previous floatingActionButton:\n', 1)
    # close the temporary comment immediately before the end of the old property block.
    marker = '            : null,\n      ),\n    );'
    if marker in s:
        s = s.replace(marker, '            : null,\n        */\n      ),\n    );', 1)
ep.write_text(s)
PY

# Remove this applicator after the real commit is created by the workflow.
