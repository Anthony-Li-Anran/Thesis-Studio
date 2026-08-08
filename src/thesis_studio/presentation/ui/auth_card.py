"""登录/注册对话框组件。复用 Prism 暗色主题令牌。"""

from nicegui import app, ui

from ...domain.exceptions import AuthConflictError, AuthCredentialError
from ...domain.models.user import User
from ...infrastructure.bootstrap import get_auth_provider
from .i18n import t
from .theme import logo

_CLOSE_ICON = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" '
    'width="18" height="18" xmlns="http://www.w3.org/2000/svg">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>'
)

_EYE_ICON = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" '
    'width="18" height="18" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639 12.27 12.27 0 015.32-6.046A12.27 12.27 0 0112 4.5c1.668 0 3.282.366 4.737 1.037a12.27 12.27 0 015.32 6.046 1.012 1.012 0 010 .639 12.27 12.27 0 01-5.32 6.046A12.27 12.27 0 0112 19.5c-1.668 0-3.282-.366-4.737-1.037a12.27 12.27 0 01-5.32-6.046z"/>'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>'
)

_EYE_OFF_ICON = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" '
    'width="18" height="18" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.241 19.5 12 19.5c.993 0 1.952-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.272 10.065 7.5a10.461 10.461 0 01-1.532 2.793m-6.218-6.218A3 3 0 1110.5 12a3 3 0 011.515-3.218z"/>'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M3 3l18 18"/></svg>'
)


def auth_card() -> ui.dialog:
    """创建登录对话框，返回 dialog 实例供外部 open()。"""
    state = {"mode": "login", "pw_visible": False}

    with ui.dialog() as dialog:
        with ui.element("div").classes("ts-dialog-card").style("width:440px;max-width:92vw"):
            with ui.element("div").classes("ts-dialog-body relative"):
                _close_button(dialog)
                title_label, subtitle_label = _header()
                name_field, name_input, email_input, password_input, eye_btn = _inputs(state)
                error_label = ui.label("").classes("ts-dialog-error")
                submit_btn = _submit_button()
                mode_label, register_link, guest_link = _links()

    _apply_mode(
        state,
        submit_btn,
        mode_label,
        register_link,
        guest_link,
        title_label,
        subtitle_label,
    )
    _wire_events(
        state,
        dialog,
        name_field,
        name_input,
        email_input,
        password_input,
        eye_btn,
        error_label,
        submit_btn,
        mode_label,
        register_link,
        guest_link,
        title_label,
        subtitle_label,
    )
    return dialog


def _close_button(dialog: ui.dialog) -> None:
    """右上角关闭按钮。"""
    btn = ui.element("div").classes("ts-dialog-close")
    btn.on("click", dialog.close)
    with btn:
        ui.html(_CLOSE_ICON)


def _header() -> tuple:
    """头部：居中 logo + 标题 + 副标题，文案由 _apply_mode 设置。"""
    with ui.element("div").classes("ts-dialog-header"):
        with ui.element("div").classes("flex justify-center mb-4"):
            logo()
        title_label = ui.label("").classes("ts-dialog-title text-center")
        subtitle_label = ui.label("").classes("ts-dialog-subtitle text-center")
    return title_label, subtitle_label


def _inputs(state: dict) -> tuple:
    """表单输入框，密码框带小眼睛切换。"""
    with ui.element("div").classes("ts-dialog-form"):
        with ui.element("div").classes("ts-dialog-field") as name_field:
            ui.label(t("auth.name")).classes("ts-dialog-label")
            name_input = (
                ui.input(placeholder=t("auth.name"))
                .classes("ts-dialog-input w-full")
                .props("dark dense")
            )
        name_field.visible = False

        with ui.element("div").classes("ts-dialog-field"):
            ui.label(t("auth.email")).classes("ts-dialog-label")
            email_input = (
                ui.input(placeholder=t("auth.email"))
                .classes("ts-dialog-input w-full")
                .props("dark dense")
            )

        with ui.element("div").classes("ts-dialog-field"):
            ui.label(t("auth.password")).classes("ts-dialog-label")
            password_input = (
                ui.input(
                    placeholder=t("auth.password"),
                    password=True,
                )
                .classes("ts-dialog-input w-full")
                .props("dark dense")
            )
            with password_input.add_slot("append"):
                eye = ui.element("button").classes("ts-eye-toggle")
                with eye:
                    ui.html(_EYE_ICON)
                eye.on("click", lambda _: _toggle_pw(state, password_input, eye))

    return name_field, name_input, email_input, password_input, eye


def _submit_button() -> ui.button:
    """主提交按钮，文案由 _apply_mode 按 mode 设置。"""
    return ui.button("").classes("ts-btn-primary w-full mt-6").props("unelevated no-caps")


def _links() -> tuple:
    """底部小字链接：注册 / 游客模式，文案由 _apply_mode 设置。"""
    with ui.element("div").classes("ts-dialog-links"):
        hint = ui.label("").classes("ts-dialog-hint")
        register = ui.label("").classes("ts-dialog-link")
        ui.label("·").classes("ts-dialog-dot")
        guest = ui.label("").classes("ts-dialog-link")
    return hint, register, guest


def _apply_mode(
    state: dict,
    submit_btn: ui.button,
    mode_label: ui.label,
    register_link: ui.label,
    guest_link: ui.label,
    title_label: ui.label,
    subtitle_label: ui.label,
) -> None:
    """按当前 mode 同步按钮与链接文案。"""
    if state["mode"] == "login":
        submit_btn.text = t("auth.login")
        mode_label.text = t("auth.no_account")
        register_link.text = t("auth.register")
        title_label.text = t("auth.signin_title")
        subtitle_label.text = t("auth.signin_subtitle")
    else:
        submit_btn.text = t("auth.register")
        mode_label.text = t("auth.have_account")
        register_link.text = t("auth.login")
        title_label.text = t("auth.register_title")
        subtitle_label.text = t("auth.register_subtitle")
    guest_link.text = t("auth.guest")


def _toggle_pw(state: dict, password: ui.input, eye: ui.element) -> None:
    """切换密码可见性。"""
    state["pw_visible"] = not state["pw_visible"]
    if state["pw_visible"]:
        password.props("type=text")
        eye.clear()
        with eye:
            ui.html(_EYE_OFF_ICON)
    else:
        password.props("type=password")
        eye.clear()
        with eye:
            ui.html(_EYE_ICON)


def _wire_events(
    state: dict,
    dialog: ui.dialog,
    name_field: ui.element,
    name_input: ui.input,
    email_input: ui.input,
    password_input: ui.input,
    eye_btn: ui.element,
    error_label: ui.label,
    submit_btn: ui.button,
    mode_label: ui.label,
    register_link: ui.label,
    guest_link: ui.label,
    title_label: ui.label,
    subtitle_label: ui.label,
) -> None:
    """绑定所有交互事件。"""

    def switch_mode() -> None:
        state["mode"] = "register" if state["mode"] == "login" else "login"
        name_field.visible = state["mode"] == "register"
        _apply_mode(
            state,
            submit_btn,
            mode_label,
            register_link,
            guest_link,
            title_label,
            subtitle_label,
        )
        error_label.text = ""

    async def on_submit() -> None:
        error_label.text = ""
        email = email_input.value.strip()
        password = password_input.value
        if not email or not password:
            error_label.text = t("auth.fill_required")
            return

        provider = get_auth_provider()
        try:
            if state["mode"] == "login":
                user = await provider.login(email, password)
            else:
                name = name_input.value.strip()
                user = await provider.register(email, password, name)
        except AuthConflictError:
            error_label.text = t("auth.conflict", email=email)
            return
        except AuthCredentialError:
            error_label.text = t("auth.credentials")
            return
        except Exception as e:  # noqa: BLE001
            error_label.text = t("auth.operation_failed", error=str(e))
            return

        _store_session(user)
        dialog.close()
        ui.navigate.reload()

    def on_guest() -> None:
        provider = get_auth_provider()
        user = provider.create_guest()
        _store_session(user)
        dialog.close()
        ui.navigate.reload()

    register_link.on("click", switch_mode)
    submit_btn.on("click", on_submit)
    guest_link.on("click", on_guest)


def _store_session(user: User) -> None:
    """将会话信息写入 NiceGUI 存储。"""
    app.storage.user["user_id"] = user.id
    app.storage.user["user_name"] = user.name
    app.storage.user["is_guest"] = user.is_guest
