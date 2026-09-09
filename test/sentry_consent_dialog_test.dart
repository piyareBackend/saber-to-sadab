import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:golden_screenshot/golden_screenshot.dart';
import 'package:sadab/data/flavor_config.dart';
import 'package:sadab/data/prefs.dart';
import 'package:sadab/data/sentry/sentry_init.dart';
import 'package:sadab/pages/home/home.dart';

void main() {
  group('SentryConsentDialog', () {
    testGoldens('', (tester) async {
      FlavorConfig.setup();
      disableSentryForTesting();
      // The consent dialog will be automatically shown if consent is unknown.
      stows.sentryConsent.value = .unknown;

      await tester.pumpWidget(
        ScreenshotApp.withConditionalTitlebar(
          device: GoldenSmallDevices.androidPhone.device,
          title: 'Saber',
          home: const HomePage(subpage: HomePage.settingsSubpage, path: ''),
        ),
      );

      await tester.loadAssets();
      await tester.pumpAndSettle();

      await expectLater(
        find.byType(MaterialApp),
        matchesGoldenFile('goldens/sentry_consent_dialog.png'),
      );
    });
  });
}
