import 'package:flutter/material.dart';

class GrayscaleWidget extends StatelessWidget {
  const GrayscaleWidget({super.key, required this.child});
  final Widget child;

  static const ColorFilter filter = ColorFilter.matrix(<double>[
    0.2126, 0.7152, 0.0722, 0, 0,
    0.2126, 0.7152, 0.0722, 0, 0,
    0.2126, 0.7152, 0.0722, 0, 0,
    0, 0, 0, 1, 0,
  ]);

  @override
  Widget build(BuildContext context) => ColorFiltered(colorFilter: filter, child: child);
}
