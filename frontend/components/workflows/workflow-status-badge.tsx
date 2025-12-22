import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { WorkflowStatus } from '@/lib/types';
import { WORKFLOW_STATUS_LABELS } from '@/lib/types';

interface WorkflowStatusBadgeProps {
  status: WorkflowStatus;
  className?: string;
}

const statusConfig: Record<WorkflowStatus, { dot: string; bg: string }> = {
  pending: {
    dot: 'bg-slate-400',
    bg: 'bg-slate-500/10 text-slate-600 dark:text-slate-400',
  },
  running: {
    dot: 'bg-blue-500 animate-pulse',
    bg: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
  },
  awaiting_approval: {
    dot: 'bg-amber-500',
    bg: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
  },
  approved: {
    dot: 'bg-emerald-500',
    bg: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
  },
  rejected: {
    dot: 'bg-red-500',
    bg: 'bg-red-500/10 text-red-600 dark:text-red-400',
  },
  completed: {
    dot: 'bg-emerald-500',
    bg: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
  },
  failed: {
    dot: 'bg-red-500',
    bg: 'bg-red-500/10 text-red-600 dark:text-red-400',
  },
};

export function WorkflowStatusBadge({ status, className }: WorkflowStatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <Badge variant="secondary" className={cn('gap-1.5 pr-2', config.bg, className)}>
      <span className={cn('h-1.5 w-1.5 rounded-full', config.dot)} />
      {WORKFLOW_STATUS_LABELS[status]}
    </Badge>
  );
}
