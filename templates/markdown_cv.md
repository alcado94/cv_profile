# {{ aboutMe.profile.name }} {{ aboutMe.profile.surnames }}
## {{ aboutMe.profile.title }}

{% if aboutMe.profile.location -%}
**{{ texts.location }}:** {{ aboutMe.profile.location.municipality or '' }}{% if aboutMe.profile.location.region %}, {{ aboutMe.profile.location.region }}{% endif %}{% if aboutMe.profile.location.country %}, {{ aboutMe.profile.location.country }}{% endif %}
{% endif %}
{% if aboutMe.relevantLinks -%}
**{{ texts.contact }}:** {% for link in aboutMe.relevantLinks %}[{{ link.type|title }}]({{ link.URL }}){% if not loop.last %} | {% endif %}{% endfor %}
{% endif %}

---

### {{ texts.about_me }}
{{ aboutMe.profile.description }}

### {{ texts.professional_experience }}
{% if total_experience_years -%}
**{{ texts.total_experience }}:** {{ total_experience_years }} {{ texts.years }}
{% endif %}

{% for job in experience.jobs -%}
{% for role in job.roles -%}
#### {{ role.name }} @ {{ job.organization.name }}
_{{ role.startDate|format_date }} - {% if role.finishDate %}{{ role.finishDate|format_date }}{% else %}{{ texts.present }}{% endif %}{% if role.startDate %} ({{ role.startDate|experience_duration(role.finishDate) }}){% endif %}_

{% if role.challenges -%}
{% for challenge in role.challenges -%}
{{ challenge.description }}
{% endfor %}
{% endif %}

{% if role.competences -%}
**{{ texts.technical_skills }}:** {{ role.competences|map(attribute='name')|join(', ') }}
{% endif %}

{% endfor %}
{% endfor %}

### {{ texts.knowledge }}

{% if knowledge.languages -%}
**{{ texts.languages }}:**
{% for language in knowledge.languages -%}
* {{ language.fullName or language.name }}{% if language.level %}: {{ language.level }}{% endif %}
{% endfor %}
{% endif %}

{% if skills_by_category -%}
**{{ texts.technical_skills }}:**
{% for category, skills in skills_by_category.items() -%}
* **{{ category }}:** {{ skills|join(', ') }}
{% endfor %}
{% endif %}

### {{ texts.training }}
{% for study in knowledge.studies -%}
* **{{ study.name }}** | {{ study.institution.name }} ({{ study.startDate|format_date }} - {% if study.finishDate %}{{ study.finishDate|format_date }}{% else %}{{ texts.in_progress }}{% endif %})
{% endfor %}
