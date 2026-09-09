import 'package:flutter/material.dart';

class GrayscaleWidget extends StatelessWidget {
  const new({super.key, required this.child});
  final child;

  static const ColorFilter filter = ColorFilter.matrix([
    0.2126,
    0.7152,
    0.0722,
    0,
    0,
    0.2126,
    0.7152,
    0.0722,
    0,
    0,
    0.2126,
    0.7152,
    0.0722,
    0,
    0,
    0,
    0,
    0,
    1,
    0,
  ]);

  @override
  Widget build(BuildContext context) =>
      ColorFiltered(colorFilter: filter, child: child);
}
