from manim import *

class Explainer(Scene):
    def construct(self):
        # Helper functions
        def show_title_card(title_text, subtitle_text=None):
            title = Text(title_text, weight=BOLD).scale(0.9)
            self.play(FadeIn(title, shift=UP, run_time=0.8))
            if subtitle_text:
                subtitle = Text(subtitle_text, font_size=36, slant=ITALIC).next_to(title, DOWN)
                self.play(Write(subtitle))
                self.wait(0.5)
                return VGroup(title, subtitle)
            self.wait(0.5)
            return VGroup(title)

        def slide(title_text, bullets, right_tags=None, emphasis_index=None, footer_note=None):
            title = Text(title_text, weight=BOLD, font_size=46)
            title.to_edge(UP)
            bullet_list = BulletedList(*bullets, font_size=32).scale(0.95)
            bullet_list.next_to(title, DOWN, buff=0.5).to_edge(LEFT, buff=0.8)
            self.play(Write(title))
            self.play(LaggedStart(*[FadeIn(m, shift=RIGHT, run_time=0.25) for m in bullet_list], lag_ratio=0.1))
            surrounds = []
            if emphasis_index is not None and 0 <= emphasis_index < len(bullets):
                target_item = bullet_list[emphasis_index]
                sr = SurroundingRectangle(target_item, color=YELLOW, buff=0.15)
                self.play(Create(sr))
                surrounds.append(sr)
                self.wait(0.3)
            tags_group = None
            if right_tags:
                tags_group = VGroup()
                for i, tag in enumerate(right_tags):
                    box = Rectangle(width=4.6, height=0.6, stroke_color=WHITE, fill_color=BLUE_E, fill_opacity=0.2)
                    label = Text(tag, font_size=28)
                    label.move_to(box.get_center())
                    tagg = VGroup(box, label)
                    if i == 0:
                        tagg.to_edge(RIGHT, buff=0.5).shift(UP*1.2)
                    else:
                        tagg.next_to(tags_group[-1], DOWN, buff=0.25).align_to(tags_group[-1], RIGHT)
                    tags_group.add(tagg)
                self.play(FadeIn(tags_group, shift=LEFT, run_time=0.6))
                # optional arrows from bullet list to first tag
                try:
                    arrow = Arrow(bullet_list.get_right() + RIGHT*0.2, tags_group.get_left() + LEFT*0.2, buff=0.2, stroke_width=3)
                    self.play(GrowArrow(arrow))
                    surrounds.append(arrow)
                except Exception:
                    pass
            footer_mob = None
            if footer_note:
                footer_mob = Text(footer_note, font_size=26, color=GREY_B).to_edge(DOWN)
                self.play(FadeIn(footer_mob, shift=UP, run_time=0.3))
            self.wait(1)
            return title, bullet_list, tags_group, surrounds, footer_mob

        def clear_slide(*mobjects):
            anims = []
            for m in mobjects:
                if m is None:
                    continue
                if isinstance(m, (list, tuple)):
                    for sub in m:
                        anims.append(FadeOut(sub))
                else:
                    anims.append(FadeOut(m))
            if anims:
                self.play(*anims)

        # Opening
        header = show_title_card("Sections 683–690 — Key Specifications Overview", "Concise explainer of construction requirements")
        self.wait(0.7)
        self.play(FadeOut(header))

        # -------------------------------
        # Section 683 — High Level Lighting Systems (Chunk 1)
        # Narration: Furnishing/installing lighting towers & high-level luminaires; ANSI/NECA 505-2010; Section 680, 920, 927; General Provisions.
        t, bl, tg, sr, ft = slide(
            "Section 683 — High Level Lighting Systems",
            bullets=[
                "Furnish and install lighting towers and high‑level luminaires per Contract.",
                "Follow ANSI/NECA 505‑2010 for high mast/roadway/area lighting.",
                "Submittals and materials per Section 680.",
                "Towers per Section 920; LED luminaires per Section 927.",
                "Delivery, storage, handling, and preparation per General Provisions."
            ],
            right_tags=[
                "ANSI/NECA 505‑2010",
                "Section 680 (Lighting Standards)",
                "Section 920 (Standards & Towers)",
                "Section 927 (LED Luminaires)",
                "General Provisions"
            ],
            emphasis_index=1,
            footer_note="Installation and maintenance must adhere to applicable standards."
        )
        # Simple cue: highlight “Standards” with a circle around the tag stack top
        if tg:
            circ = Circle(radius=0.5, color=YELLOW).move_to(tg[0])
            self.play(Create(circ))
            sr.append(circ)
        self.wait(0.5)
        clear_slide(t, bl, tg, sr, ft)

        # -------------------------------
        # Section 683 — High Level Lighting Systems (Chunk 2)
        # Narration: Follow Section 680 for construction/QA/warranty; General Provisions for fabrication/measurement/limits/adjustments; Payment per each (towers with lowering equipment, luminaires by type/source, lowering device PSU).
        t, bl, tg, sr, ft = slide(
            "Section 683 — Construction, Acceptance, Payment",
            bullets=[
                "Construction, quality acceptance, and warranty per Section 680.",
                "Fabrication, measurement, limits, adjustments per General Provisions.",
                "Payment (each): towers w/ lowering gear; luminaires (type & source); lowering device PSU."
            ],
            right_tags=["Section 680", "General Provisions", "Payment: Each"],
            emphasis_index=2,
            footer_note="Complete requirements referenced to Section 680 and General Provisions."
        )
        # Visual cue: a downward arrow to a “Payment: Each” tag
        if tg:
            pay_tag = tg[-1]
            arrow = Arrow(t.get_bottom() + DOWN*0.2, pay_tag.get_top(), stroke_width=4)
            self.play(GrowArrow(arrow))
            sr.append(arrow)
        self.wait(0.5)
        clear_slide(t, bl, tg, sr, ft)

        # -------------------------------
        # Section 685 — Blast Cleaning PCC Structures (Chunk 1)
        # Narration: Scope; remove residue; equipment & traffic control per Contract & MUTCD; dust containment or water; PPE & respirators.
        t, bl, tg, sr, ft = slide(
            "Section 685 — Blast Cleaning PCC Structures",
            bullets=[
                "Blast clean PCC surfaces; promptly remove blasting residue.",
                "Use proper equipment and traffic control (Contract + MUTCD).",
                "Control dust: enclosure or water spray at nozzles.",
                "PPE: eye & hearing protection; respirators/forced‑air hoods in dusty areas."
            ],
            right_tags=["MUTCD", "Dust Control", "Worker Protection"],
            emphasis_index=2,
            footer_note="Protect road users and the environment during cleaning operations."
        )
        # Simple visuals: a small “dust” cloud and a shield for PPE
        dust = Circle(radius=0.4, color=GREY_B, fill_opacity=0.2).next_to(bl, RIGHT, buff=1.2).shift(UP*0.7)
        dust_label = Text("Dust", font_size=24, color=GREY_B).move_to(dust.get_center())
        ppe = RegularPolygon(5, color=GREEN, fill_opacity=0.1).scale(0.5).next_to(dust, DOWN, buff=0.6)
        ppe_label = Text("PPE", font_size=24, color=GREEN).move_to(ppe.get_center())
        self.play(FadeIn(VGroup(dust, dust_label, ppe, ppe_label), shift=LEFT, run_time=0.6))
        sr.extend([dust, dust_label, ppe, ppe_label])
        self.wait(0.5)
        clear_slide(t, bl, tg, sr, ft)

        # -------------------------------
        # Section 685 — Methods, Finish, Measurement (Chunk 2)
        # Narration: Methods (dry/wet, compressed air/centrifugal, recovery); air traps; near traffic residue removal and dust control; stop if unsafe; uniform finish <=1% remnants, match photos; inspection & re-blast; measurement by area & linear mile (each face separately).
        t, bl, tg, sr, ft = slide(
            "Section 685 — Methods, Finish, Measurement",
            bullets=[
                "Methods: dry/wet abrasive; compressed air or centrifugal wheels; optional recovery.",
                "Compressed air: traps to keep oil/grease off cleaned surface.",
                "Within 10 ft of live traffic: remove residue immediately, control dust, stop if unsafe.",
                "Finish: uniform; only minute remnants in pits; ≤1% of any square yard; match Dept. photos.",
                "Inspection: correct deficiencies by re‑blasting at no additional cost.",
                "Measurement: area for structures; linear mile for variable‑height barriers; each face separately."
            ],
            right_tags=["Safety Near Traffic", "Uniform Finish ≤1%", "Measurement Rules"],
            emphasis_index=3,
            footer_note="Quality and safety drive acceptance; re‑blast if required."
        )
        # Highlight the "≤1%" with a rectangle
        if len(bl) >= 4:
            rect = SurroundingRectangle(bl[3], color=ORANGE, buff=0.15)
            self.play(Create(rect))
            sr.append(rect)
        self.wait(0.5)
        clear_slide(t, bl, tg, sr, ft)

        # -------------------------------
        # Section 685 — Payment (Chunk 3)
        # Narration: Contract unit price covers all; items by square yard (meter) and linear mile (kilometer).
        t, bl, tg, sr, ft = slide(
            "Section 685 — Payment",
            bullets=[
                "Paid at Contract unit price for full compliance with specification.",
                "Items: cleaning PCC structures — by square yard (meter).",
                "Variable‑height concrete median barriers — by linear mile (kilometer)."
            ],
            right_tags=["Unit Pay Items"],
            emphasis_index=0,
            footer_note="Measurement units differ by item type."
        )
        pay_box = Rectangle(width=5.5, height=1.0, color=YELLOW, fill_opacity=0.1).next_to(bl, RIGHT, buff=1.0)
        pay_text = Text("Contract Unit Price", font_size=30, color=YELLOW).move_to(pay_box.get_center())
        self.play(FadeIn(VGroup(pay_box, pay_text), shift=LEFT))
        sr.extend([pay_box, pay_text])
        self.wait(0.5)
        clear_slide(t, bl, tg, sr, ft)

        # -------------------------------
        # Section 686 — Radio Tower Antenna
        # Narration: Specifications provided elsewhere in the Contract.
        t, bl, tg, sr, ft = slide(
            "Section 686 — Radio Tower Antenna",
            bullets=[
                "Detailed specifications are provided elsewhere in the Contract."
            ],
            right_tags=["See Project‑Specific Docs"],
            emphasis_index=0,
            footer_note="Consult the Contract for full antenna requirements."
        )
        self.wait(0.5)
        clear_slide(t, bl, tg, sr, ft)

        # -------------------------------
        # Section 687 — Traffic Signal Timing
        # Narration: Specifications provided elsewhere in the Contract.
        t, bl, tg, sr, ft = slide(
            "Section 687 — Traffic Signal Timing",
            bullets=[
                "Detailed specifications are provided elsewhere in the Contract."
            ],
            right_tags=["See Project‑Specific Docs"],
            emphasis_index=0,
            footer_note="Refer to the Contract timing plans and procedures."
        )
        self.wait(0.5)
        clear_slide(t, bl, tg, sr, ft)

        # -------------------------------
        # Section 688 — Motorist Aid Call Box
        # Narration: Specifications provided elsewhere in the Contract.
        t, bl, tg, sr, ft = slide(
            "Section 688 — Motorist Aid Call Box",
            bullets=[
                "Detailed specifications are provided elsewhere in the Contract."
            ],
            right_tags=["See Project‑Specific Docs"],
            emphasis_index=0,
            footer_note="Follow site‑specific plans and vendor documentation."
        )
        self.wait(0.5)
        clear_slide(t, bl, tg, sr, ft)

        # -------------------------------
        # Section 690 — Static Scale System (Chunk)
        # Narration: Furnish/install 3‑axle static scale; NIST HB 44 + Dept. sections; submittals after award with 60‑day review; catalogs/diagrams/performance data; transferable guarantees & manuals; contractor warranty before work.
        t, bl, tg, sr, ft = slide(
            "Section 690 — Static Scale System",
            bullets=[
                "Furnish/install a three‑axle static scale system per plans/specs and NIST HB 44.",
                "After award: submit materials list, shop drawings, equipment data; allow 60 days for review.",
                "Provide manufacturer catalogs, diagrams, and performance data (not just model numbers).",
                "Submit transferable manufacturer guarantees and O&M manuals.",
                "Before work: provide written contractor warranty as specified."
            ],
            right_tags=["NIST Handbook 44", "Submittals (60 days)", "Guarantees & O&M", "Contractor Warranty"],
            emphasis_index=0,
            footer_note="All documentation must be complete and reviewable by the Department."
        )
        # Simple system sketch: platform + 3 axle indicators
        platform = Rectangle(width=6.0, height=0.4, color=BLUE_C, fill_opacity=0.1).to_edge(DOWN, buff=1.2).shift(LEFT*0.5)
        ax1 = Circle(radius=0.15, color=BLUE_C, fill_opacity=0.6).next_to(platform.get_top(), UP, buff=0.15).align_to(platform, LEFT).shift(RIGHT*0.6)
        ax2 = ax1.copy().shift(RIGHT*1.8)
        ax3 = ax2.copy().shift(RIGHT*1.8)
        labels = Text("3‑Axle Static Scale", font_size=28, color=BLUE_C).next_to(platform, UP, buff=0.2)
        self.play(FadeIn(VGroup(platform, ax1, ax2, ax3, labels), shift=UP, run_time=0.8))
        self.wait(0.5)
        clear_slide(t, bl, tg, sr, ft)

        # Closing card
        end = show_title_card("End of Explainer", "Refer to the Contract and referenced Sections for full requirements.")
        self.play(FadeOut(end, run_time=0.8))
        self.wait(0.2)


if __name__ == '__main__':
    scene = Explainer()
    scene.render() # That's it!