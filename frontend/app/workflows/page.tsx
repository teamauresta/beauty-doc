'use client';

import Link from 'next/link';
import { Plus, Workflow } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { PageHeader } from '@/components/layout/page-header';
import { WorkflowCard } from '@/components/workflows/workflow-card';
import { useWorkflows } from '@/lib/hooks';

export default function WorkflowsPage() {
  const { data: workflows, isLoading, error } = useWorkflows();

  return (
    <div>
      <PageHeader title="工作流" description="查看和管理您的增长任务">
        <Link href="/workflows/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            创建任务
          </Button>
        </Link>
      </PageHeader>

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-[100px] rounded-lg" />
          ))}
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
          加载失败，请刷新页面重试
        </div>
      )}

      {workflows && workflows.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-16">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
            <Workflow className="h-6 w-6 text-muted-foreground" />
          </div>
          <h3 className="mt-4 text-lg font-medium">暂无任务</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            创建您的第一个增长任务
          </p>
          <Link href="/workflows/new" className="mt-4">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              创建任务
            </Button>
          </Link>
        </div>
      )}

      {workflows && workflows.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {workflows.map((workflow) => (
            <WorkflowCard key={workflow.id} workflow={workflow} />
          ))}
        </div>
      )}
    </div>
  );
}
