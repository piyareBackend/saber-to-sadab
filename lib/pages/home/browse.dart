import 'dart:async';

import 'package:collapsible/collapsible.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:go_router/go_router.dart';
import 'package:path/path.dart' as p;
import 'package:sadab/components/home/delete_note_button.dart';
import 'package:sadab/components/home/export_note_button.dart';
import 'package:sadab/components/home/folder_sidebar.dart';
import 'package:sadab/components/home/grid_folders.dart';
import 'package:sadab/components/home/home_layout_button.dart';
import 'package:sadab/components/home/masonry_files.dart';
import 'package:sadab/components/home/move_note_button.dart';
import 'package:sadab/components/home/new_note_button.dart';
import 'package:sadab/components/home/no_files.dart';
import 'package:sadab/components/home/path_components.dart';
import 'package:sadab/components/home/rename_note_button.dart';
import 'package:sadab/components/home/sort_button.dart';
import 'package:sadab/components/home/syncing_button.dart';
import 'package:sadab/data/file_manager/file_manager.dart';
import 'package:sadab/data/prefs.dart';
import 'package:sadab/data/routes.dart';
import 'package:sadab/i18n/strings.g.dart';

class BrowsePage extends StatefulHookWidget {
  const new({super.key, String? path}) : initialPath = path;

  final String? initialPath;

  @visibleForTesting
  static DirectoryChildren? overrideChildren;

  @override
  State<BrowsePage> createState() => _BrowsePageState();
}

class _BrowsePageState extends State<BrowsePage> {
  DirectoryChildren? children;
  String? path;
  final ValueNotifier<List<String>> selectedFiles = ValueNotifier([]);

  @override
  void initState() {
    path = widget.initialPath;
    findChildrenOfPath();
    fileWriteSubscription = FileManager.fileWriteStream.stream.listen(fileWriteListener);
    selectedFiles.addListener(_setState);
    super.initState();
  }

  @override
  void dispose() {
    selectedFiles.removeListener(_setState);
    fileWriteSubscription?.cancel();
    super.dispose();
  }

  StreamSubscription? fileWriteSubscription;

  void fileWriteListener(FileOperation event) {
    if (!event.filePath.startsWith(path ?? '/')) return;
    findChildrenOfPath(fromFileListener: true);
  }

  void _setState() => setState(() {});

  Future<void> findChildrenOfPath({bool fromFileListener = false}) async {
    if (!mounted) return;
    if (fromFileListener) {
      final location = GoRouterState.of(context).uri.toString();
      if (!location.startsWith(RoutePaths.prefixOfHome)) return;
    }
    children = BrowsePage.overrideChildren ??
        await FileManager.getChildrenOfDirectory(
          path ?? '/',
          sortMetric: stows.browseSortMetric.value,
        );
    if (mounted) setState(() {});
  }

  void onDirectoryTap(String folder) {
    selectedFiles.value = [];
    if (folder == '..') {
      path = p.dirname(path ?? '/');
      if (path == '/') path = null;
    } else {
      path = p.join(path ?? '/', folder);
    }
    context.go(HomeRoutes.browseFilePath(path ?? '/'));
    findChildrenOfPath();
  }

  void onPathComponentTap(String? newPath) {
    selectedFiles.value = [];
    if (newPath == null || newPath.isEmpty || newPath == '/') newPath = null;
    path = newPath;
    context.go(HomeRoutes.browseFilePath(path ?? '/'));
    findChildrenOfPath();
  }

  Future<void> createFolder(String folderName) async {
    final folderPath = '${path ?? ''}/$folderName';
    await FileManager.createFolder(folderPath);
    findChildrenOfPath();
  }

  Future<void> _openFolderManager() async {
    final currentChildren = children;
    if (currentChildren == null || !mounted) return;
    await showModalBottomSheet<void>(
      context: context,
      useSafeArea: true,
      showDragHandle: true,
      isScrollControlled: true,
      builder: (_) => SizedBox(
        height: MediaQuery.sizeOf(context).height * .72,
        child: FolderSidebar(
          path: path,
          folders: currentChildren.directories,
          onFolderTap: (folder) {
            Navigator.of(context).pop();
            if (folder.isEmpty) {
              onPathComponentTap(null);
            } else {
              onDirectoryTap(folder);
            }
          },
          onCreateFolder: createFolder,
          doesFolderExist: (name) => currentChildren.directories.contains(name),
          onRenameFolder: (oldName, newName) async {
            await FileManager.renameDirectory('${path ?? ''}/$oldName', newName);
            await findChildrenOfPath();
          },
          onDeleteFolder: (name) async {
            await FileManager.deleteDirectory('${path ?? ''}/$name');
            await findChildrenOfPath();
          },
          isFolderEmpty: (name) async {
            final result = await FileManager.getChildrenOfDirectory('${path ?? ''}/$name');
            return result?.isEmpty ?? true;
          },
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = ColorScheme.of(context);
    final platform = Theme.of(context).platform;
    final screenWidth = MediaQuery.sizeOf(context).width;
    final crossAxisCount = screenWidth ~/ 300 + 1;
    final showSidebar = screenWidth >= 900;
    useListenable(stows.homeLayout);
    useOnListenableChange(stows.browseSortMetric, findChildrenOfPath);

    final content = CustomScrollView(
      slivers: [
        SliverAppBar(
          collapsedHeight: kToolbarHeight,
          expandedHeight: 168,
          pinned: true,
          scrolledUnderElevation: 1,
          flexibleSpace: FlexibleSpaceBar(
            title: Text(
              t.home.titles.browse,
              style: TextStyle(color: colorScheme.onSurface),
            ),
            centerTitle: false,
            titlePadding: const EdgeInsetsDirectional.only(start: 16, bottom: 8),
          ),
          actions: [
            if (!showSidebar)
              IconButton(
                tooltip: 'Folders',
                onPressed: _openFolderManager,
                icon: const Icon(Icons.folder_copy_outlined),
              ),
            const BrowseSortButton(),
            const HomeLayoutButton(),
            const SyncingButton(),
          ],
        ),
        SliverToBoxAdapter(
          child: PathComponents(path, onPathComponentTap: onPathComponentTap),
        ),
        const SliverPadding(padding: EdgeInsets.only(bottom: 12)),
        GridFolders(
          isAtRoot: path?.isEmpty ?? true,
          crossAxisCount: crossAxisCount,
          onTap: onDirectoryTap,
          createFolder: createFolder,
          doesFolderExist: (String folderName) => children?.directories.contains(folderName) ?? false,
          renameFolder: (String oldName, String newName) async {
            await FileManager.renameDirectory('${path ?? ''}/$oldName', newName);
            await findChildrenOfPath();
          },
          isFolderEmpty: (String folderName) async {
            final result = await FileManager.getChildrenOfDirectory('${path ?? ''}/$folderName');
            return result?.isEmpty ?? true;
          },
          deleteFolder: (String folderName) async {
            await FileManager.deleteDirectory('${path ?? ''}/$folderName');
            await findChildrenOfPath();
          },
          folders: [for (final directoryPath in children?.directories ?? const []) directoryPath],
        ),
        if (children == null) ...[
          // loading
        ] else if (children!.isEmpty) ...[
          const SliverSafeArea(sliver: SliverToBoxAdapter(child: NoFiles())),
        ] else ...[
          SliverSafeArea(
            top: false,
            minimum: const EdgeInsets.only(top: 8, bottom: 70),
            sliver: MasonryFiles(
              crossAxisCount: crossAxisCount,
              files: [for (final filePath in children?.files ?? const []) '${path ?? ''}/$filePath'],
              selectedFiles: selectedFiles,
            ),
          ),
        ],
      ],
    );

    return Scaffold(
      body: showSidebar
          ? Row(
              children: [
                FolderSidebar(
                  path: path,
                  folders: children?.directories ?? const [],
                  onFolderTap: (folder) {
                    if (folder.isEmpty) {
                      onPathComponentTap(null);
                    } else {
                      onDirectoryTap(folder);
                    }
                  },
                  onCreateFolder: createFolder,
                  doesFolderExist: (name) => children?.directories.contains(name) ?? false,
                  onRenameFolder: (oldName, newName) async {
                    await FileManager.renameDirectory('${path ?? ''}/$oldName', newName);
                    await findChildrenOfPath();
                  },
                  onDeleteFolder: (name) async {
                    await FileManager.deleteDirectory('${path ?? ''}/$name');
                    await findChildrenOfPath();
                  },
                  isFolderEmpty: (name) async {
                    final result = await FileManager.getChildrenOfDirectory('${path ?? ''}/$name');
                    return result?.isEmpty ?? true;
                  },
                ),
                const VerticalDivider(width: 1),
                Expanded(child: content),
              ],
            )
          : content,
      floatingActionButton: NewNoteButton(
        cupertino: platform.isCupertino,
        path: path,
      ),
      persistentFooterButtons: selectedFiles.value.isEmpty
          ? null
          : [
              Collapsible(
                axis: CollapsibleAxis.vertical,
                collapsed: selectedFiles.value.length != 1,
                child: RenameNoteButton(
                  existingPath: selectedFiles.value.first,
                  unselectNotes: () => selectedFiles.value = [],
                ),
              ),
              MoveNoteButton(
                filesToMove: selectedFiles.value,
                unselectNotes: () => selectedFiles.value = [],
              ),
              DeleteNoteButton(
                filesToDelete: selectedFiles.value,
                unselectNotes: () => selectedFiles.value = [],
              ),
              ExportNoteButton(selectedFiles: selectedFiles.value),
            ],
    );
  }
}
