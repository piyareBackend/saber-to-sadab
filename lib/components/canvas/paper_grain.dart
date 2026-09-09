import 'package:flutter/material.dart';

class PaperGrainPainter extends CustomPainter {
  const new();
  static final _points = List<Offset>.generate(420, (i) {
    final x = ((i * 73) % 997) / 997.0;
    final y = ((i * 181 + 31) % 991) / 991.0;
    return Offset(x, y);
  }, growable: false);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = Colors.black.withValues(alpha: 0.022);
    for (final point in _points) {
      canvas.drawCircle(
        Offset(point.dx * size.width, point.dy * size.height),
        0.45,
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant PaperGrainPainter oldDelegate) => false;
}

class PaperGrain extends StatelessWidget {
  const new({super.key});
  @override
  Widget build(BuildContext context) => const IgnorePointer(
    child: RepaintBoundary(child: CustomPaint(painter: PaperGrainPainter())),
  );
}
