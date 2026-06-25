import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:muscle_selector/muscle_selector.dart';

import 'package:example/main.dart';

// Tiny in-memory body so the example loads without the real (>50KB) asset.
const _fixture = '<svg xmlns="http://www.w3.org/2000/svg">\n'
    '<path id="human_body" title="human_body" class="muscle" d="M0,0 L100,0 L100,200 L0,200 Z"/>\n'
    '<path id="chest1" title="chest1" class="muscle" d="M10,10 L40,10 L40,40 L10,40 Z"/>\n'
    '<path id="chest2" title="chest2" class="muscle" d="M60,10 L90,10 L90,40 L60,40 Z"/>\n'
    '<path id="neck" title="neck" class="muscle" d="M40,0 L60,0 L60,10 L40,10 Z"/>\n'
    '</svg>';

void main() {
  testWidgets('shows a Male/Female toggle and the picker, and switching '
      'gender does not error', (tester) async {
    final messenger = tester.binding.defaultBinaryMessenger;
    messenger.setMockMessageHandler('flutter/assets', (ByteData? message) async {
      final bytes = Uint8List.fromList(utf8.encode(_fixture));
      return ByteData.view(bytes.buffer);
    });
    addTearDown(() => messenger.setMockMessageHandler('flutter/assets', null));

    await tester.pumpWidget(MyApp());
    await tester.pumpAndSettle();

    expect(find.text('Male'), findsOneWidget);
    expect(find.text('Female'), findsOneWidget);
    expect(find.byType(MusclePickerMap), findsOneWidget);

    await tester.tap(find.text('Female'));
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
  });
}
