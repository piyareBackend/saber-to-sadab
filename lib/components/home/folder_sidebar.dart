import 'package:flutter/material.dart';
import 'package:sadab/components/home/delete_folder_button.dart';
import 'package:sadab/components/home/new_folder_dialog.dart';
import 'package:sadab/components/home/rename_folder_button.dart';

class FolderSidebar extends StatelessWidget {
  const FolderSidebar({
    super.key,
    required this.path,
    required this.folders,
    required this.onFolderTap,
    required this.onCreateFolder,
    required this.doesFolderExist,
    required this.onRenameFolder,
    required this.onDeleteFolder,
    required this.isFolderEmpty,
  });

  final String? path;
  final List<String> folders;
  final ValueChanged<String> onFolderTap;
  final ValueChanged<String> onCreateFolder;
  final bool Function(String) doesFolderExist;
  final Future<void> Function(String oldName, String newName) onRenameFolder;
  final Future<void> Function(String) onDeleteFolder;
  final Future<bool> Function(String) isFolderEmpty;

  Future<void> _newFolder(BuildContext context) async {
    await showDialog<void>(
      context: context,
      builder: (_) => NewFolderDialog(
        createFolder: onCreateFolder,
        doesFolderExist: doesFolderExist,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final scheme = ColorScheme.of(context);
    final currentLabel = path == null || path!.isEmpty ? 'All Notes' : path!.split('/').last;

    return Material(
      color: scheme.surfaceContainerLow,
      child: SizedBox(
        width: 272,
        child: SafeArea(
          right: false,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(18, 18, 12, 8),
                child: Row(
                  children: [
                    Icon(Icons.folder_copy_outlined, color: scheme.primary),
                    const SizedBox(width: 10),
                    const Expanded(
                      child: Text(
                        'Folders',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                      ),
                    ),
                    IconButton(
                      tooltip: 'New folder',
                      onPressed: () => _newFolder(context),
                      icon: const Icon(Icons.create_new_folder_outlined),
                    ),
                  ],
                ),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 10),
                child: Card(
                  margin: EdgeInsets.zero,
                  elevation: 0,
                  color: scheme.primaryContainer,
                  child: ListTile(
                    dense: true,
                    leading: Icon(Icons.notes_outlined, color: scheme.onPrimaryContainer),
                    title: Text(
                      'All Notes',
                      style: TextStyle(color: scheme.onPrimaryContainer, fontWeight: FontWeight.w600),
                    ),
                    selected: path == null,
                    onTap: () => onFolderTap(''),
                  ),
                ),
              ),
              const SizedBox(height: 8),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 18),
                child: Text(
                  currentLabel,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontSize: 12, color: scheme.onSurfaceVariant),
                ),
              ),
              const SizedBox(height: 4),
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.fromLTRB(10, 0, 10, 16),
                  itemCount: folders.length,
                  itemBuilder: (context, index) {
                    final folder = folders[index];
                    return ListTile(
                      dense: true,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      leading: Icon(Icons.folder_outlined, color: scheme.primary),
                      title: Text(folder, maxLines: 1, overflow: TextOverflow.ellipsis),
                      onTap: () => onFolderTap(folder),
                      trailing: PopupMenuButton<String>(
                        tooltip: 'Folder actions',
                        onSelected: (action) async {
                          if (action == 'rename') {
                            await showDialog<void>(
                              context: context,
                              builder: (_) => RenameFolderButton(
                                folderName: folder,
                                doesFolderExist: doesFolderExist,
                                renameFolder: (newName) => onRenameFolder(folder, newName),
                              ),
                            );
                          } else if (action == 'delete') {
                            await onDeleteFolder(folder);
                          }
                        },
                        itemBuilder: (_) => const [
                          PopupMenuItem(value: 'rename', child: Text('Rename')),
                          PopupMenuItem(value: 'delete', child: Text('Delete')),
                        ],
                        icon: const Icon(Icons.more_horiz, size: 20),
                      ),
                    );
                  },
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(12),
                child: Text(
                  'Tip: long folders can be renamed or removed from their menu.',
                  style: TextStyle(fontSize: 11, color: scheme.onSurfaceVariant),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
