import 'dart:math' as math;
import 'package:flutter/material.dart';

enum ShapeKind { line, arrow, doubleArrow, rectangle, roundedRect, ellipse, axes, triangle, star }
enum ShapeFill { transparent, translucent, solid }
enum ShapeStrokeStyle { solid, dotted, dashed }

class CustomShapeDefinition {
  const CustomShapeDefinition({required this.id, required this.label, required this.kind, this.fill = ShapeFill.transparent, this.strokeStyle = ShapeStrokeStyle.solid, this.lineWeight = 3});
  final String id; final String label; final ShapeKind kind;
  final ShapeFill fill; final ShapeStrokeStyle strokeStyle; final double lineWeight;
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
