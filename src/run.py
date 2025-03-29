from main import QuickCalc, create_tray_icon

if __name__ == "__main__":
    app = QuickCalc()
    create_tray_icon(app)
    app.run()
