import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:sadab/data/file_manager/file_manager.dart';
import 'package:sadab/data/flavor_config.dart';
import 'package:sadab/data/nextcloud/nextcloud_client_extension.dart';
import 'package:sadab/data/nextcloud/saber_syncer.dart';
import 'package:sadab/data/prefs.dart';

import 'utils/test_mock_channel_handlers.dart';
import 'utils/test_random.dart';

void main() {
  final username = Platform.environment['SADAB_NC_USERNAME'];
  final password = Platform.environment['SADAB_NC_PASSWORD'];
  final serverUrl = Platform.environment['SADAB_NC_URL'];
  final hasIntegrationConfig =
      username != null && username.isNotEmpty &&
      password != null && password.isNotEmpty &&
      serverUrl != null && serverUrl.isNotEmpty;

  test(
    'Upload and download file',
    () async {
      TestWidgetsFlutterBinding.ensureInitialized();
      HttpOverrides.global = null;
      setupMockPathProvider();
      setupMockFlutterSecureStorage();

      FileManager.documentsDirectory =
          '$tmpDir/nc_upload_download_test/'
          '${FileManager.appRootDirectoryPrefix}';
      FlavorConfig.setup();
      await FileManager.init();

      stows.url.value = serverUrl!;
      stows.username.value = username!;
      stows.ncPassword.value = password!;
      stows.encPassword.value = username;

      final client = SaberSyncInterface.client!;
      await client.loadEncryptionKey();

      final localFile = FileManager.getFile('/helloworld${randomString(10)}.txt');
      final syncFile = await syncer.interface.getSyncFileFromLocalFile(localFile);
      printOnFailure(syncFile.toString());
      expect(syncFile.remotePath, matches(RegExp(r'^Saber/[a-zA-Z0-9]+\.sbe$')));

      const content = 'Hello, world!';
      await localFile.create(recursive: true);
      await localFile.writeAsString(content);

      final upBytes = await syncer.interface.readLocalFile(syncFile);
      expect(upBytes, isNotEmpty);
      await syncer.interface.uploadRemoteFile(syncFile, upBytes);

      final remoteFile = await syncer.interface.getWebDavFile(
        syncFile.remotePath,
      );
      if (remoteFile == null) fail('Remote file not found after upload');
      final syncFile2 = await syncer.interface.getSyncFileFromRemoteFile(
        remoteFile,
      );
      expect(syncFile2, equals(syncFile));

      final downBytes = await syncer.interface.downloadRemoteFile(syncFile);
      expect(downBytes, isNotEmpty);
      expect(downBytes, equals(upBytes));
      await syncer.interface.writeLocalFile(
        syncFile,
        downBytes,
        awaitWrite: true,
      );
      expect(await localFile.readAsString(), equals(content));
    },
    skip: hasIntegrationConfig
        ? false
        : 'Nextcloud integration credentials are not configured in CI',
    retry: 2,
  );
}
