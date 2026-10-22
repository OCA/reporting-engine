import {CodeEditor} from "@web/core/code_editor/code_editor";
import {patch} from "@web/core/utils/patch";

patch(CodeEditor, {
    MODES: [...CodeEditor.MODES, "pgsql"],
});
