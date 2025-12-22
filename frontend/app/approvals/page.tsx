'use client';

import { CheckCircle } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { PageHeader } from '@/components/layout/page-header';
import { ApprovalCard } from '@/components/approvals/approval-card';
import { usePendingApprovals } from '@/lib/hooks';

export default function ApprovalsPage() {
  const { data: approvals, isLoading, error } = usePendingApprovals();

  return (
    <div>
      <PageHeader
        title="待审核"
        description="审核AI生成的内容和策略"
      />

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-[160px] rounded-lg" />
          ))}
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
          加载失败，请刷新页面重试
        </div>
      )}

      {approvals && approvals.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-16">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10">
            <CheckCircle className="h-6 w-6 text-emerald-600" />
          </div>
          <h3 className="mt-4 text-lg font-medium">暂无待审核</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            所有内容都已审核完成
          </p>
        </div>
      )}

      {approvals && approvals.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {approvals.map((approval) => (
            <ApprovalCard key={approval.workflow_id} approval={approval} />
          ))}
        </div>
      )}
    </div>
  );
}
