from difflib import SequenceMatcher, ndiff
import re

from IPython.display import HTML, display
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from herbarium_processor.config import ROOT_DIR


class CsvComparator:
    def __init__(self, canonical_csv_path: str, test_csv_path: str):
        self.canonical_csv_path = ROOT_DIR / canonical_csv_path
        self.test_csv_path = ROOT_DIR / test_csv_path

        canon = pd.read_csv(canonical_csv_path, dtype=str)
        test = pd.read_csv(test_csv_path, dtype=str)
        canon.columns = canon.columns.str.strip().str.lower()
        test.columns = test.columns.str.strip().str.lower()

        canon_id_column = "imagename" if "imagename" in canon.columns else "id"
        test_id_column = "imagename" if "imagename" in test.columns else "id"
        if canon_id_column not in canon.columns or test_id_column not in test.columns:
            raise ValueError(
                "Both CSV files must include an 'id' or 'imagename' column."
            )

        canon = canon.rename(columns={canon_id_column: "id"})
        test = test.rename(columns={test_id_column: "id"})

        canon["id"] = canon["id"].astype(str).str.strip()
        test["id"] = test["id"].astype(str).str.strip()

        shared_columns = [
            col for col in test.columns if col in canon.columns and col != "id"
        ]
        self.comparison_columns = shared_columns

        canon_sub = canon[["id"] + shared_columns].copy()
        test_sub = test[["id"] + shared_columns].copy()

        canon_sub = canon_sub.sort_values("id").reset_index(drop=True)
        test_sub = test_sub.sort_values("id").reset_index(drop=True)

        self.merged = pd.merge(
            canon_sub, test_sub, on="id", suffixes=("_canon", "_test")
        )

        self.test_csv = self.merged[
            ["id"] + [f"{col}_test" for col in shared_columns]
        ].rename(columns=lambda c: c.replace("_test", ""))
        self.canonical_csv = self.merged[
            ["id"] + [f"{col}_canon" for col in shared_columns]
        ].rename(columns=lambda c: c.replace("_canon", ""))

        self.row_correct_counts = [0] * len(self.merged)
        self.accuracy_report = {}
        self.total_correct = 0
        self.summary_df = None

    def normalize(self, val, normalize_more=False):
        if pd.isna(val):
            return ""
        val = str(val).strip()
        val = re.sub(r"\bfeet\b", "ft", val)
        if normalize_more:
            val = val.lower()
            val = re.sub(
                r"[\s\W_\u00ba]+", "", val
            )  # \u00ba = º (masculine ordinal indicator, treated as word char in Unicode regex)
        return val

    def compare_fields(self, val1, val2):
        return self.normalize(val1, True) == self.normalize(val2, True)

    def evaluate(self, verbose: bool = True):
        total_rows = len(self.merged)
        self.row_correct_counts = [0] * total_rows
        self.accuracy_report = {}
        self.total_correct = 0

        for column in self.comparison_columns:
            correct = 0
            diffs = []
            for i in range(total_rows):
                val1 = self.merged.at[i, f"{column}_canon"]
                val2 = self.merged.at[i, f"{column}_test"]
                match = self.compare_fields(val1, val2)
                if match:
                    correct += 1
                    self.row_correct_counts[i] += 1
                elif len(diffs) < 5:
                    diffs.append(
                        {
                            "id": self.merged.at[i, "id"],
                            "original": self.normalize(val1),
                            "test": self.normalize(val2),
                        }
                    )
            self.total_correct += correct
            self.accuracy_report[column] = {
                "correct": correct,
                "total": total_rows,
                "accuracy": round(correct / total_rows, 3),
                "examples": diffs,
            }

        total_fields = total_rows * len(self.comparison_columns)
        self.total_accuracy = round(self.total_correct / total_fields, 3)
        self.summary_df = pd.DataFrame.from_dict(
            {
                col: {"accuracy": v["accuracy"]}
                for col, v in self.accuracy_report.items()
            },
            orient="index",
        )

        if verbose:
            print("\n🧠 Model Similarity Summary")
            print(
                f"✅ Percentage of identical fields: {self.total_accuracy * 100:.1f}%\n"
            )
            print("📊 Per column identical:")
            display(self.summary_df)
        return self.summary_df

    def visualize(self, show: bool = True):
        summary_df = self.summary_df
        fig1 = plt.figure(figsize=(6, 4))
        sns.barplot(x=summary_df.index, y=summary_df["accuracy"])
        plt.title("Model identical by Field")
        plt.ylabel("Identical Percentage")
        plt.xlabel("Field")
        plt.ylim(0, 1)
        plt.xticks(rotation=45)
        plt.tight_layout()
        if show:
            plt.show()
        return fig1

    def display_sample_diffs(self, display_inline: bool = True):
        html_parts = []
        toggle_script = """
<button onclick="toggleSampleDiffView()">Toggle Diff View</button>
<script>
function toggleSampleDiffView() {
    const origTables = document.querySelectorAll('.sample-orig-table');
    const diffTables = document.querySelectorAll('.sample-diff-table');
    for (let i = 0; i < origTables.length; i++) {
        if (origTables[i].style.display === 'none') {
            origTables[i].style.display = '';
            diffTables[i].style.display = 'none';
        } else {
            origTables[i].style.display = 'none';
            diffTables[i].style.display = '';
        }
    }
}
</script>
"""
        tables_html = []
        for col, data in self.accuracy_report.items():
            if data["examples"]:
                orig_rows = []
                diff_rows = []
                for ex in data["examples"]:
                    arrow_view = (
                        f"{ex['test']}<br><small><i>→ {ex['original']}</i></small>"
                    )
                    diff_view = self.inline_diff(ex["test"], ex["original"])
                    orig_rows.append(
                        f"<tr><td style='padding:4px;'>{ex['id']}</td>"
                        f"<td style='padding:4px;'>{ex['test']}</td>"
                        f"<td style='padding:4px;'>{ex['original']}</td></tr>"
                    )
                    diff_rows.append(
                        f"<tr><td style='padding:4px;'>{ex['id']}</td>"
                        f"<td style='padding:4px;' colspan='2'>"
                        f"<span class='arrow-view' style='display:none'>{arrow_view}</span>"
                        f"<span class='diff-view'>{diff_view}<br><small><i>→ {ex['original']}</i></small></span>"
                        f"</td></tr>"
                    )
                table_html = f"<h4>❌ Sample Mismatches in Column: {col}</h4>"
                table_html += "<table class='sample-orig-table' border='1' style='border-collapse:collapse;font-family:sans-serif;font-size:14px;'>"
                table_html += "<tr><th style='padding:4px;'>ID</th><th style='padding:4px;'>Test Value</th><th style='padding:4px;'>Canonical Value</th></tr>"
                table_html += "".join(orig_rows)
                table_html += "</table>"
                table_html += "<table class='sample-diff-table' border='1' style='border-collapse:collapse;font-family:sans-serif;font-size:14px; display:none;'>"
                table_html += "<tr><th style='padding:4px;'>ID</th><th style='padding:4px;' colspan='2'>Diff (test vs canonical)</th></tr>"
                table_html += "".join(diff_rows)
                table_html += "</table>"
                tables_html.append(table_html)
        if display_inline:
            if tables_html:
                html = toggle_script + "".join(tables_html)
                display(HTML(html))
        else:
            if tables_html:
                html_parts.append(toggle_script)
                html_parts.extend(tables_html)
            return "\n".join(html_parts)

    def similarity(self, a, b):
        return SequenceMatcher(None, self.normalize(a), self.normalize(b)).ratio()

    def inline_diff(self, a, b):
        a = self.normalize(a)
        b = self.normalize(b)
        diff = list(ndiff(a, b))
        result = ""
        for part in diff:
            if part.startswith("-"):
                result += f'<span style="background-color:#ffcccc">{part[2:]}</span>'
            elif part.startswith("+"):
                result += f'<span style="background-color:#ccffcc">{part[2:]}</span>'
            elif part.startswith(" "):
                result += part[2:]
        return result

    def highlight_diffs(self, row):
        styled = []
        for col in self.comparison_columns:
            test_val = self.merged.at[row.name, f"{col}_test"]
            canon_val = self.merged.at[row.name, f"{col}_canon"]
            test_val_norm = "" if pd.isna(test_val) else test_val
            canon_val_norm = "" if pd.isna(canon_val) else canon_val
            sim = self.similarity(test_val, canon_val)
            if sim == 1:
                style = "background-color: #e6ffe6; color: #000; padding: 4px;"
                display_val = test_val_norm
            else:
                red = int((1 - sim) * 255)
                color = f"#{255:02x}{255 - red:02x}{128:02x}"
                style = f"background-color: {color}; color: #000; font-weight: bold; padding: 4px;"
                arrow_view = (
                    f"{test_val_norm}<br><small><i>→ {canon_val_norm}</i></small>"
                )
                diff_view = self.inline_diff(test_val, canon_val)
                display_val = f"<span class='arrow-view'>{arrow_view}</span><span class='diff-view' style='display:none'>{diff_view}<br><small><i>→ {canon_val_norm}</i></small></span>"
            styled.append(f'<td style="{style}">{display_val}</td>')
        link = f'<a href="https://lichenportal.org/portal/collections/individual/index.php?occid={row["id"]}" target="_blank">🔗</a>'
        return (
            f'<tr><td style="padding: 4px;"><b>{row["id"]}</b><br>{link}</td>'
            + "".join(styled)
            + "</tr>"
        )

    def display_diff_view(self, return_html: bool = False):
        html = """<button onclick="toggleDiffView()">Toggle Diff View</button>
<script>
function toggleDiffView() {
    const arrow = document.querySelectorAll('.arrow-view');
    const diff = document.querySelectorAll('.diff-view');
    for (let i = 0; i < arrow.length; i++) {
        if (arrow[i].style.display === 'none') {
            arrow[i].style.display = 'inline';
            diff[i].style.display = 'none';
        } else {
            arrow[i].style.display = 'none';
            diff[i].style.display = 'inline';
        }
    }
}
</script>
"""
        html += '<table border="1" style="border-collapse: collapse; font-family: sans-serif; font-size: 14px;">'
        html += (
            '<tr><th style="padding: 6px;">ID</th>'
            + "".join(
                [
                    f'<th style="padding: 6px;">{col}</th>'
                    for col in self.comparison_columns
                ]
            )
            + "</tr>"
        )
        html += "\n".join(self.merged.apply(self.highlight_diffs, axis=1))
        html += "</table>"
        if return_html:
            return html
        display(HTML(html))

    def calculate_html_parts(self):
        self.evaluate(verbose=False)
        html_parts = [
            "<h2>Model Similarity Summary</h2>",
            f"<p>Total Identical Fields: {self.total_accuracy * 100:.1f}%</p>",
            "<h3>Identical Entries Per-Field</h3>",
            self.summary_df.rename(columns={"accuracy": "identical"}).to_html(border=1),
        ]
        fig1 = self.visualize(show=False)
        import base64
        import io

        buf = io.BytesIO()
        fig1.savefig(buf, format="png")
        encoded1 = base64.b64encode(buf.getvalue()).decode()
        buf.close()
        html_parts.append(f"<img src='data:image/png;base64,{encoded1}'/>")

        sample_html = self.display_sample_diffs(display_inline=False)
        if sample_html:
            html_parts.append("<h3>Sample Mismatches</h3>")
            html_parts.append(sample_html)
        html_parts.append("<h3>Diff View</h3>")
        html_parts.append(self.display_diff_view(return_html=True))
        return html_parts
