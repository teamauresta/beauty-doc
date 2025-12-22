import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { WorkflowStatusBadge } from './workflow-status-badge';
import type { Workflow } from '@/lib/types';
import { WORKFLOW_TYPE_LABELS } from '@/lib/types';

interface WorkflowCardProps {
  workflow: Workflow;
}

export function WorkflowCard({ workflow }: WorkflowCardProps) {
  const timeAgo = formatDistanceToNow(new Date(workflow.created_at), {
    addSuffix: true,
    locale: zhCN,
  });

  return (
    <Link href={`/workflows/${workflow.id}`}>
      <Card className="cursor-pointer transition-all hover:shadow-md hover:border-foreground/20">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <span className="font-medium">
              {WORKFLOW_TYPE_LABELS[workflow.workflow_type]}
            </span>
            <WorkflowStatusBadge status={workflow.status} />
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>{timeAgo}</span>
            {workflow.current_step && (
              <span className="truncate max-w-[150px]">
                {workflow.current_step}
              </span>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
