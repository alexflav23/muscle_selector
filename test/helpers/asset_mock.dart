import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

// Small, self-contained SVG fixtures (<50KB so AssetBundle.loadString takes the
// synchronous utf8 path and never spawns a compute() isolate under fake-async).
const _human =
    '<path id="human_body" title="human_body" class="muscle" d="M0,0 L100,0 L100,200 L0,200 Z"/>';
const _chest1 =
    '<path id="chest1" title="chest1" class="muscle" d="M10,10 L40,10 L40,40 L10,40 Z"/>';
const _chest2 =
    '<path id="chest2" title="chest2" class="muscle" d="M60,10 L90,10 L90,40 L60,40 Z"/>';
const _neck =
    '<path id="neck" title="neck" class="muscle" d="M40,0 L60,0 L60,10 L40,10 Z"/>';
const _biceps1 =
    '<path id="biceps1" title="biceps1" class="muscle" d="M0,50 L20,50 L20,90 L0,90 Z"/>';
const _biceps2 =
    '<path id="biceps2" title="biceps2" class="muscle" d="M80,50 L100,50 L100,90 L80,90 Z"/>';

String svgOf(List<String> paths) =>
    '<svg xmlns="http://www.w3.org/2000/svg">\n${paths.join('\n')}\n</svg>';

/// male body fixture: chest group + neck
final String maleFixtureSvg = svgOf([_human, _chest1, _chest2, _neck]);

/// female body fixture: same as male PLUS a biceps group (used to prove a
/// gender switch actually reloads a different asset).
final String femaleFixtureSvg =
    svgOf([_human, _chest1, _chest2, _neck, _biceps1, _biceps2]);

const chestPath = _chest1;
const chest2Path = _chest2;
const humanPath = _human;

// A chest1 whose path covers the whole 100x200 map, so a tap at the layout
// centre is guaranteed to land inside it (the painter hit-tests against the
// muscle path, not a bounding box).
const fullChest1 =
    '<path id="chest1" title="chest1" class="muscle" d="M0,0 L100,0 L100,200 L0,200 Z"/>';

/// Intercept `rootBundle` asset loads and serve in-memory SVG fixtures.
/// female SVGs (key ends with `human_body_female.svg`) get [female], else [male].
void mockMuscleAssets(WidgetTester tester, {String? male, String? female}) {
  final maleSvg = male ?? maleFixtureSvg;
  final femaleSvg = female ?? femaleFixtureSvg;
  final messenger = tester.binding.defaultBinaryMessenger;
  messenger.setMockMessageHandler('flutter/assets', (ByteData? message) async {
    final key = utf8.decode(
        message!.buffer.asUint8List(message.offsetInBytes, message.lengthInBytes));
    final svg = key.endsWith('human_body_female.svg') ? femaleSvg : maleSvg;
    final bytes = Uint8List.fromList(utf8.encode(svg));
    return ByteData.view(bytes.buffer);
  });
  rootBundle.clear();
  addTearDown(() {
    messenger.setMockMessageHandler('flutter/assets', null);
    rootBundle.clear();
  });
}
