import flet as ft
from flet import Colors, Padding
from core.data import load_data, save_data, create_folder, add_item, delete_folder, remove_item
from core.opener import open_item
import os
from tkinter import Tk, filedialog


def run():
    def main(page: ft.Page):
        page.title = "File Linker"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 0

        data = load_data()
        current_folder = None

        folders_list = ft.ListView(expand=1, spacing=5, padding=10)
        items_grid = ft.GridView(expand=1, runs_count=6, max_extent=120, child_aspect_ratio=1.0, spacing=10,
                                 run_spacing=10, padding=10)

        current_folder_title = ft.Text("Выберите папку слева", size=20, weight=ft.FontWeight.BOLD)

        add_root_folder_btn = ft.Button("📁 Создать папку", icon=ft.Icons.CREATE_NEW_FOLDER,
                                        style=ft.ButtonStyle(color=Colors.WHITE, bgcolor=Colors.BLUE_700))
        add_subfolder_btn = ft.Button("📁 Создать подпапку", icon=ft.Icons.CREATE_NEW_FOLDER,
                                      style=ft.ButtonStyle(color=Colors.WHITE, bgcolor=Colors.INDIGO_700),
                                      disabled=True)
        add_item_btn = ft.Button("➕ Добавить элемент", icon=ft.Icons.ADD,
                                 style=ft.ButtonStyle(color=Colors.WHITE, bgcolor=Colors.GREEN_700), disabled=True)
        back_btn = ft.IconButton(icon=ft.Icons.ARROW_BACK, tooltip="Вернуться на главную", visible=False)

        def show_dialog(dlg):
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        def close_dialog(dlg):
            dlg.open = False
            page.update()

        def render_folders():
            folders_list.controls.clear()
            for coll in data["collections"]:
                tile = ft.ListTile(
                    leading=ft.Text(coll["icon"], size=24),
                    title=ft.Text(coll["name"], weight=ft.FontWeight.W_500),
                    subtitle=ft.Text(f"{len(coll['items'])} элементов", size=12),
                    data=coll,
                    on_click=on_folder_click
                )
                folders_list.controls.append(
                    ft.GestureDetector(
                        content=tile,
                        on_secondary_tap=lambda e, c=coll: show_folder_menu(c, is_root=True)
                    )
                )
            page.update()

        def render_items(folder):
            nonlocal current_folder
            current_folder = folder

            if folder is None:
                current_folder_title.value = "Выберите папку слева"
                back_btn.visible = False
                add_subfolder_btn.disabled = True
                add_item_btn.disabled = True
                items_grid.controls.clear()
                items_grid.controls.append(ft.Text("Справа будут отображаться файлы", color=Colors.GREY_600))
            else:
                current_folder_title.value = f"{folder.get('icon', '📁')} {folder['name']}"
                back_btn.visible = True
                add_subfolder_btn.disabled = False
                add_item_btn.disabled = False

                items_grid.controls.clear()
                if not folder["items"]:
                    items_grid.controls.append(
                        ft.Text("Папка пуста. Добавьте файлы или подпапки.", color=Colors.GREY_500))
                else:
                    for item in folder["items"]:
                        # ИСПРАВЛЕНИЕ 1: Берем иконку из данных элемента, если она есть
                        icon = item.get("icon")

                        if not icon:
                            icon = "📄"
                            if item["type"] == "url":
                                icon = "🌐"
                            elif item["type"] == "note":
                                icon = "📌"
                            elif item["type"] == "subfolder":
                                icon = "📁"

                        card_content = ft.Container(
                            content=ft.Column([
                                ft.Text(icon, size=40),
                                ft.Text(item.get("name", "Без имени"), size=12, text_align=ft.TextAlign.CENTER,
                                        max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)
                            ], alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor=Colors.GREY_800,
                            border_radius=8,
                            padding=10,
                        )

                        card = ft.GestureDetector(
                            content=card_content,
                            on_double_tap=lambda e, it=item: handle_open(it),
                            on_secondary_tap=lambda e, it=item: show_item_menu(it)
                        )
                        items_grid.controls.append(card)
            page.update()

        def on_folder_click(e):
            render_items(e.control.data)

        def go_back(e):
            render_items(None)

        def handle_open(item):
            if item["type"] == "subfolder":
                render_items(item)
            elif item["type"] == "note":
                dlg = ft.AlertDialog(title=ft.Text(item.get("name", "Заметка")),
                                     content=ft.Text(item.get("body", "Пусто")))
                show_dialog(dlg)
            else:
                open_item(item)

        def show_folder_menu(folder, is_root=False):
            def edit_click(e):
                close_dialog(menu_dlg)
                show_edit_dialog(folder, is_folder=True)

            def delete_click(e):
                close_dialog(menu_dlg)
                if is_root:
                    delete_folder(data, folder["id"])
                    if current_folder and current_folder["id"] == folder["id"]:
                        go_back(None)
                    save_data(data)
                    render_folders()
                else:
                    confirm_delete_item(folder)

            menu_dlg = ft.AlertDialog(
                title=ft.Text(f"Действия: {folder['name']}"),
                content=ft.Column([
                    ft.ListTile(leading=ft.Icon(ft.Icons.EDIT), title=ft.Text("Переименовать"), on_click=edit_click),
                    ft.ListTile(leading=ft.Icon(ft.Icons.DELETE, color=Colors.RED_400),
                                title=ft.Text("Удалить", color=Colors.RED_400), on_click=delete_click),
                ], tight=True),
            )
            show_dialog(menu_dlg)

        def show_item_menu(item):
            def edit_click(e):
                close_dialog(menu_dlg)
                show_edit_dialog(item, is_folder=(item["type"] == "subfolder"))

            def open_click(e):
                close_dialog(menu_dlg)
                handle_open(item)

            def delete_click(e):
                close_dialog(menu_dlg)
                confirm_delete_item(item)

            menu_dlg = ft.AlertDialog(
                title=ft.Text(f"Действия: {item.get('name', 'Элемент')}"),
                content=ft.Column([
                    ft.ListTile(leading=ft.Icon(ft.Icons.OPEN_IN_BROWSER), title=ft.Text("Открыть"),
                                on_click=open_click),
                    ft.ListTile(leading=ft.Icon(ft.Icons.EDIT), title=ft.Text("Редактировать"), on_click=edit_click),
                    ft.ListTile(leading=ft.Icon(ft.Icons.DELETE, color=Colors.RED_400),
                                title=ft.Text("Удалить", color=Colors.RED_400), on_click=delete_click),
                ], tight=True),
            )
            show_dialog(menu_dlg)

        def show_left_empty_menu(e):
            show_create_folder_dialog(is_subfolder=False)

        def show_right_empty_menu(e):
            if not current_folder: return

            def create_folder_click(ev):
                close_dialog(menu_dlg)
                show_create_folder_dialog(is_subfolder=True)

            def add_item_click(ev):
                close_dialog(menu_dlg)
                show_add_item_dialog(None)

            menu_dlg = ft.AlertDialog(
                title=ft.Text("Действия в папке"),
                content=ft.Column([
                    ft.ListTile(leading=ft.Icon(ft.Icons.CREATE_NEW_FOLDER), title=ft.Text("Создать подпапку"),
                                on_click=create_folder_click),
                    ft.ListTile(leading=ft.Icon(ft.Icons.ADD), title=ft.Text("Добавить элемент (файл/ссылку)"),
                                on_click=add_item_click),
                ], tight=True),
            )
            show_dialog(menu_dlg)

        def confirm_delete_item(item):
            def delete_yes(e):
                if current_folder:
                    remove_item(current_folder, item["id"])
                    if current_folder["id"] == item["id"]:
                        go_back(None)
                    else:
                        render_items(current_folder)
                save_data(data)
                render_folders()
                close_dialog(dlg)

            dlg = ft.AlertDialog(
                title=ft.Text("Удалить?"),
                content=ft.Text("Элемент удалится из программы (оригинал на диске останется)."),
                actions=[
                    ft.TextButton("Отмена", on_click=lambda e: close_dialog(dlg)),
                    ft.FilledButton("Удалить", on_click=delete_yes, style=ft.ButtonStyle(bgcolor=Colors.RED_700)),
                ]
            )
            show_dialog(dlg)

        def show_create_folder_dialog(e=None, is_subfolder=False):
            name_input = ft.TextField(label="Название папки", autofocus=True)
            icon_input = ft.Dropdown(
                label="Иконка", value="📁",
                options=[
                    ft.dropdown.Option("📁", "📁 Папка"),
                    ft.dropdown.Option("💼", "💼 Работа"),
                    ft.dropdown.Option("📚", "📚 Учёба"),
                    ft.dropdown.Option("🎬", "🎬 Видео"),
                    ft.dropdown.Option("⭐", "⭐ Избранное"),
                ]
            )

            def save_folder(ev):
                if not name_input.value:
                    name_input.error_text = "Введите название"
                    page.update()
                    return

                create_folder(data, current_folder if is_subfolder else None, name_input.value, icon_input.value)
                save_data(data)

                if is_subfolder:
                    render_items(current_folder)
                else:
                    render_folders()
                close_dialog(dlg)

            dlg = ft.AlertDialog(
                title=ft.Text("Создать подпапку" if is_subfolder else "Создать папку"),
                content=ft.Column([name_input, icon_input], tight=True, width=300),
                actions=[
                    ft.TextButton("Отмена", on_click=lambda e: close_dialog(dlg)),
                    ft.FilledButton("Создать", on_click=save_folder),
                ]
            )
            show_dialog(dlg)

        def show_add_item_dialog(e):
            if not current_folder: return

            type_dropdown = ft.Dropdown(
                options=[ft.dropdown.Option("file", "Файл"), ft.dropdown.Option("url", "Ссылка (URL)"),
                         ft.dropdown.Option("note", "Заметка")],
                value="file", label="Тип элемента"
            )
            name_input = ft.TextField(label="Название")
            path_input = ft.TextField(label="Путь к файлу", expand=True)

            def pick_file_local(ev):
                root = Tk();
                root.withdraw();
                root.attributes('-topmost', True)
                file_path = filedialog.askopenfilename(title="Выберите файл")
                root.destroy()
                if file_path: path_input.value = file_path; page.update()

            browse_btn = ft.IconButton(icon=ft.Icons.FOLDER, on_click=pick_file_local)
            file_row = ft.Row([path_input, browse_btn], visible=True)
            url_input = ft.TextField(label="Ссылка (URL)", visible=False)
            note_body = ft.TextField(label="Текст заметки", multiline=True, min_lines=3, visible=False)

            def on_type_change(ev):
                if type_dropdown.value == "note":
                    file_row.visible, url_input.visible, note_body.visible = False, False, True
                elif type_dropdown.value == "url":
                    file_row.visible, url_input.visible, note_body.visible = False, True, False
                else:
                    file_row.visible, url_input.visible, note_body.visible = True, False, False
                page.update()

            type_dropdown.on_change = on_type_change

            def save_item(ev):
                item_type = type_dropdown.value
                name = name_input.value or None

                if item_type == "note":
                    if not note_body.value: return
                    add_item(current_folder, "note", name=name or "Заметка", body=note_body.value)
                elif item_type == "url":
                    target = url_input.value
                    if not target.startswith(
                        ("http://", "https://")): url_input.error_text = "Неверный URL"; page.update(); return
                    add_item(current_folder, "url", name=name or target, target=target)
                else:
                    target = path_input.value
                    if not target: return
                    add_item(current_folder, "file", name=name or os.path.basename(target), target=target)

                save_data(data);
                render_items(current_folder);
                render_folders();
                close_dialog(dlg)

            dlg = ft.AlertDialog(
                title=ft.Text("Добавить элемент"),
                content=ft.Column([type_dropdown, name_input, file_row, url_input, note_body], tight=True),
                actions=[ft.TextButton("Отмена", on_click=lambda e: close_dialog(dlg)),
                         ft.FilledButton("Добавить", on_click=save_item)]
            )
            show_dialog(dlg)

        def show_edit_dialog(item, is_folder=False):
            name_input = ft.TextField(label="Название", value=item.get("name", ""))
            body_input = ft.TextField(label="Текст", multiline=True, min_lines=3,
                                      value=item.get("body", "")) if item.get("type") == "note" else None

            def save_edit(e):
                item["name"] = name_input.value
                if body_input: item["body"] = body_input.value
                save_data(data)

                render_folders()
                if current_folder: render_items(current_folder)
                close_dialog(dlg)

            content = [name_input, body_input] if body_input else [name_input]
            dlg = ft.AlertDialog(
                title=ft.Text("Редактировать"),
                content=ft.Column(content, tight=True),
                actions=[ft.TextButton("Отмена", on_click=lambda e: close_dialog(dlg)),
                         ft.FilledButton("Сохранить", on_click=save_edit)]
            )
            show_dialog(dlg)

        add_root_folder_btn.on_click = lambda e: show_create_folder_dialog(is_subfolder=False)
        add_subfolder_btn.on_click = lambda e: show_create_folder_dialog(is_subfolder=True)
        add_item_btn.on_click = show_add_item_dialog
        back_btn.on_click = go_back

        render_folders()

        page.add(
            ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("ПАПКИ", size=14, weight=ft.FontWeight.BOLD, color=Colors.GREY_400,
                                    margin=Padding.only(left=10, top=10)),
                            ft.GestureDetector(
                                content=ft.Container(content=folders_list, expand=True),
                                on_secondary_tap=show_left_empty_menu
                            )
                        ]),
                        width=300,
                        bgcolor=Colors.GREY_900,
                        border_radius=ft.BorderRadius(top_left=10, bottom_left=10, top_right=0, bottom_right=0)
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                back_btn,
                                current_folder_title,
                            ], alignment=ft.MainAxisAlignment.START, spacing=10, height=50),
                            ft.Divider(height=1),
                            ft.GestureDetector(
                                content=ft.Container(content=items_grid, expand=True),
                                on_secondary_tap=show_right_empty_menu
                            )
                        ]),
                        expand=True,
                        bgcolor=Colors.SURFACE_CONTAINER_LOWEST,
                        border_radius=ft.BorderRadius(top_right=10, bottom_right=10, top_left=0, bottom_left=0)
                    )
                ], expand=True),

                ft.Container(
                    content=ft.Row([
                        ft.Row([add_root_folder_btn], width=300),
                        ft.Row([add_subfolder_btn, add_item_btn], expand=True, spacing=10)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=15,
                    bgcolor=Colors.GREY_900
                )
            ], spacing=0, expand=True)
        )

    ft.run(main)