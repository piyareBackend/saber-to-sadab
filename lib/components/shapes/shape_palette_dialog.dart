import 'package:flutter/material.dart';
import 'package:sadab/components/shapes/custom_shape_engine.dart';

class ShapePaletteDialog extends StatefulWidget {
  const ShapePaletteDialog({super.key, required this.onSelected});
  final ValueChanged<CustomShapeDefinition> onSelected;
  @override State<ShapePaletteDialog> createState() => _ShapePaletteDialogState();
}

class _ShapePaletteDialogState extends State<ShapePaletteDialog> {
  ShapeFill fill = ShapeFill.transparent; ShapeStrokeStyle stroke = ShapeStrokeStyle.solid; double weight = 3;
  IconData iconFor(ShapeKind kind) => switch (kind) {
    ShapeKind.line => Icons.horizontal_rule, ShapeKind.arrow => Icons.arrow_forward, ShapeKind.doubleArrow => Icons.swap_horiz,
    ShapeKind.rectangle => Icons.crop_square, ShapeKind.roundedRect => Icons.rounded_corner, ShapeKind.ellipse => Icons.circle_outlined,
    ShapeKind.axes => Icons.center_focus_strong, ShapeKind.triangle => Icons.change_history, ShapeKind.star => Icons.star_border,
  };
  @override
  Widget build(BuildContext context) => AlertDialog(
    title: const Text('Shapes'),
    content: SizedBox(width: 420, child: Column(mainAxisSize: MainAxisSize.min, children: [
      GridView.builder(shrinkWrap: true, gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, crossAxisSpacing: 8, mainAxisSpacing: 8), itemCount: CustomShapeRegistry.defaults.length, itemBuilder: (_, i) {
        final shape = CustomShapeRegistry.defaults[i];
        return OutlinedButton(onPressed: () { widget.onSelected(CustomShapeDefinition(id: shape.id, label: shape.label, kind: shape.kind, fill: fill, strokeStyle: stroke, lineWeight: weight)); Navigator.pop(context); }, child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(iconFor(shape.kind)), Text(shape.label, textAlign: TextAlign.center, style: const TextStyle(fontSize: 11))]));
      }),
      const SizedBox(height: 12),
      SegmentedButton<ShapeFill>(segments: const [ButtonSegment(value: ShapeFill.transparent, label: Text('Clear')), ButtonSegment(value: ShapeFill.translucent, label: Text('Glass')), ButtonSegment(value: ShapeFill.solid, label: Text('Solid'))], selected: {fill}, onSelectionChanged: (v) => setState(() => fill = v.first)),
      SegmentedButton<ShapeStrokeStyle>(segments: const [ButtonSegment(value: ShapeStrokeStyle.solid, label: Text('Solid')), ButtonSegment(value: ShapeStrokeStyle.dotted, label: Text('Dotted')), ButtonSegment(value: ShapeStrokeStyle.dashed, label: Text('Dashed'))], selected: {stroke}, onSelectionChanged: (v) => setState(() => stroke = v.first)),
      Row(children: [const Text('Weight'), Expanded(child: Slider(min: 1, max: 12, divisions: 11, value: weight, onChanged: (v) => setState(() => weight = v)))])
    ])),
  );
}
