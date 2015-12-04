from __future__ import absolute_import

from sentry.api.bases import OrganizationMemberEndpoint
from sentry.api.serializers import serialize
from sentry.api.paginator import DateTimePaginator
from sentry.models import Group, OrganizationMemberTeam, Project


class OrganizationMemberIssuesBookmarkedEndpoint(OrganizationMemberEndpoint):
    def get(self, request, organization, member):
        """
        Return a list of issues assigned to the given member.
        """
        project_list = Project.objects.filter(
            organization=organization,
            team__in=OrganizationMemberTeam.objects.filter(
                organizationmember=member,
                is_active=True,
            ).values('team')
        )

        queryset = Group.objects.filter(
            bookmark_set__user=member.user,
            bookmark_set__project__in=project_list,
        ).extra(
            select={'sort_by': 'sentry_groupbookmark.date_added'},
        ).order_by('-sort_by')

        return self.paginate(
            request=request,
            queryset=queryset,
            order_by='-sort_by',
            paginator_cls=DateTimePaginator,
            on_results=lambda x: serialize(x, request.user),
        )