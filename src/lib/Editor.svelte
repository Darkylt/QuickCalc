<script lang="ts">
  import { onMount } from "svelte";
  import { EditorView, keymap, highlightActiveLine } from "@codemirror/view";
  import { EditorState } from "@codemirror/state";
  import { javascript } from "@codemirror/lang-javascript";
  import { autocompletion, CompletionContext } from "@codemirror/autocomplete";
  import { invoke } from "@tauri-apps/api/core";

  let editorDiv: HTMLDivElement;
  let editor: EditorView;

  async function evaluateExpression(expr: string): Promise<number> {
    return invoke<number>("eval_math", { expression: expr });
  }

  function getMathExpressionAtCursor(doc: string, cursorPos: number): { from: number; to: number; expr: string } | null {
    const beforeCursor = doc.slice(0, cursorPos);
    const eqIndex = beforeCursor.lastIndexOf("=");
    if (eqIndex === -1) return null;

    const expr = beforeCursor.slice(eqIndex + 1).trim();
    if (!/^[0-9+\-*/().\s]+$/.test(expr)) return null;

    return { from: eqIndex + 1, to: cursorPos, expr };
  }

  function provideMathCompletion() {
    return autocompletion({
      override: [
        async (context: CompletionContext) => {
          const doc = context.state.doc.toString();
          const math = getMathExpressionAtCursor(doc, context.pos);
          if (!math) return null;

          try {
            const result = await evaluateExpression(math.expr);
            return {
              from: math.from,
              to: math.to,
              options: [
                {
                  label: result.toString(),
                  type: "keyword",
                  apply: (view, completion, from, to) => {
                    view.dispatch({
                      changes: { from, to, insert: result.toString() },
                      selection: { anchor: from + result.toString().length },
                    });
                  },
                },
              ],
            };
          } catch {
            return null;
          }
        },
      ],
    });
  }

  onMount(() => {
    editor = new EditorView({
      state: EditorState.create({
        doc: "",
        extensions: [
          javascript(),
          keymap.of([]),
          highlightActiveLine(),
          provideMathCompletion(),
        ],
      }),
      parent: editorDiv,
    });
  });
</script>

<div bind:this={editorDiv} style="height: 100%; width: 100%;"></div>
