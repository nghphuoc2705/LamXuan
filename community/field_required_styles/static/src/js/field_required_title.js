document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".o_wrap_field").forEach((wrapEl) => {
        const inputEl = wrapEl.querySelector(".o_required_modifier input");
        const labelEl = wrapEl.querySelector("label");

        if (inputEl) {
            const initialValue = inputEl.value?.trim() || "";
            if (initialValue === "") {
                inputEl.classList.add("field_required_input");
                debugger; // ← giữ nguyên nếu bạn cần debug tại đây
                if (labelEl) {
                    labelEl.classList.add("field_required_label");
                }
            } else {
                inputEl.classList.remove("field_required_input");
                if (labelEl) {
                    labelEl.classList.remove("field_required_label");
                }
            }
        }
    });
});
