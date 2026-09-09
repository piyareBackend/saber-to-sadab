import 'package:flutter/material.dart';

class FloatingToolbox extends StatefulWidget {
  const new({
    super.key,
    required this.onPenPreset,
    required this.onEraser,
    required this.onUndo,
    required this.onRedo,
    required this.onPalmRejection,
    required this.onShapes,
  });
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
  var palm = true;

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.sizeOf(context);
    final maxX = (size.width - 330).clamp(8.0, double.infinity);
    final maxY = (size.height - 90).clamp(8.0, double.infinity);
    position = Offset(
      position.dx.clamp(8.0, maxX),
      position.dy.clamp(8.0, maxY),
    );
    return Transform.translate(
      offset: position,
      child: GestureDetector(
        onPanUpdate: (d) => setState(() => position += d.delta),
        child: Material(
          elevation: 8,
          color: Theme.of(context).colorScheme.surface.withValues(alpha: .94),
          shape: const StadiumBorder(),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                ...[1, 2, 3].map((i) => _b('P$i', () => widget.onPenPreset(i))),
                _b('E', widget.onEraser),
                _b('↶', widget.onUndo),
                _b('↷', widget.onRedo),
                _b('◇', widget.onShapes),
                IconButton(
                  tooltip: 'Palm rejection',
                  isSelected: palm,
                  onPressed: () {
                    setState(() => palm = !palm);
                    widget.onPalmRejection(palm);
                  },
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
    child: IconButton.filledTonal(
      onPressed: onPressed,
      icon: Text(
        text,
        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
      ),
    ),
  );
}
