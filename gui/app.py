import flet as ft
from flet import Colors, Padding
from core.data import load_data, save_data, create_folder


def run():
    def main(page: ft.Page):
        page.title = "File Linker"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 20

        data = load_data()

        folders_list = ft.ListView(expand=1, spacing=10, padding=20, width=250)
        items_grid = ft.GridView(expand=1, runs_count=5, max_extent=150, child_aspect_ratio=1.0, spacing=10,
                                 run_spacing=10)
        current_folder_title = ft.Text("Выберите папку слева", size=24, weight=ft.FontWeight.BOLD)

        def on_folder_click(e):
            folder_id = e.control.data
            folder = next((c for c in data["collections"] if c["id"] == folder_id), None)

            if folder:
                current_folder_title.value = f"{folder['icon']} {folder['name']}"
                items_grid.controls.clear()

                if not folder["items"]:
                    items_grid.controls.append(ft.Text("В этой папке пока пусто", color=Colors.GREY))
                else:
                    for item in folder["items"]:
                        icon = "📄"
                        if item["type"] == "url":
                            icon = "🌐"
                        elif item["type"] == "note":
                            icon = "📌"
                        elif item["type"] == "subfolder":
                            icon = "📁"

                        items_grid.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(icon, size=40),
                                    ft.Text(item.get("name", "Без имени"), size=14, max_lines=2,
                                            overflow=ft.TextOverflow.ELLIPSIS)
                                ], alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                bgcolor=Colors.SURFACE_VARIANT,
                                border_radius=10,
                                padding=10,
                            )
                        )
                page.update()

        for coll in data["collections"]:
            folders_list.controls.append(
                ft.ListTile(
                    leading=ft.Text(coll["icon"], size=24),
                    title=ft.Text(coll["name"]),
                    subtitle=ft.Text(f"{len(coll['items'])} элементов"),
                    data=coll["id"],
                    on_click=on_folder_click
                )
            )

        def add_folder_click(e):
            new_id = create_folder(data, None, "Новая папка")
            save_data(data)
            folders_list.controls.append(
                ft.ListTile(
                    leading=ft.Text("📁", size=24),
                    title=ft.Text("Новая папка"),
                    subtitle=ft.Text("0 элементов"),
                    data=new_id,
                    on_click=on_folder_click
                )
            )
            page.update()

        add_btn = ft.Button(
            "➕ Новая папка",
            on_click=add_folder_click,
            style=ft.ButtonStyle(color=Colors.WHITE, bgcolor=Colors.BLUE_700)
        )

        page.add(
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("ПАПКИ", size=16, weight=ft.FontWeight.BOLD, color=Colors.GREY),
                        folders_list,
                        add_btn
                    ]),
                    width=300,
                    bgcolor=Colors.SURFACE,
                    border_radius=10,
                    padding=10
                ),
                ft.Container(
                    content=ft.Column([
                        current_folder_title,
                        ft.Divider(),
                        items_grid
                    ]),
                    expand=True,
                    padding=Padding.only(left=20)
                )
            ], expand=True)
        )

    ft.run(main)