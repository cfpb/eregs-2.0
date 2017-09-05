from django.views.generic import TemplateView

from eregs_core.models import Preamble, Version


class MainView(TemplateView):
    template_name = 'eregs_core/main.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)

        reg_versions = Version.objects.exclude(version=None)
        meta = [
            r for r in Preamble.objects.filter(
                tag='preamble',
                reg_version__in=reg_versions
            )
        ]

        regs_meta = []
        reg_parts = set()

        for item in meta:
            item.get_descendants(auto_infer_class=False)
            if (item.cfr_title, item.cfr_section) not in reg_parts:
                regs_meta.append(item)
                reg_parts.add((item.cfr_title, item.cfr_section))

        regs_meta = sorted(
            regs_meta,
            key=lambda x: (int(x.cfr_title), int(x.cfr_section))
        )

        context.update({
            'preamble': regs_meta,
        })

        return context
