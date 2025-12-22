'use client';

import { use, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { toast } from 'sonner';
import { ArrowLeft, Check, X, MessageSquare, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { PageHeader } from '@/components/layout/page-header';
import { ContentPreview } from '@/components/approvals/content-preview';
import { useWorkflow, useWorkflowState } from '@/lib/hooks';
import { submitApproval } from '@/lib/api';
import { WORKFLOW_TYPE_LABELS } from '@/lib/types';
import type { ApprovalDecision } from '@/lib/types';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function ApprovalReviewPage({ params }: PageProps) {
  const { id } = use(params);
  const router = useRouter();
  const { workflow, isLoading } = useWorkflow(id);
  const { state } = useWorkflowState(id);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [confirmDialog, setConfirmDialog] = useState<{
    open: boolean;
    decision: ApprovalDecision | null;
  }>({ open: false, decision: null });

  const handleSubmit = async (decision: ApprovalDecision) => {
    if (decision === 'request_changes' && !feedback.trim()) {
      toast.error('请填写修改意见');
      return;
    }

    setIsSubmitting(true);
    try {
      await submitApproval(id, {
        decision,
        feedback: feedback.trim() || undefined,
      });

      toast.success(
        decision === 'approve'
          ? '已批准'
          : decision === 'reject'
          ? '已拒绝'
          : '已请求修改'
      );
      router.push('/approvals');
      router.refresh();
    } catch (error) {
      toast.error('操作失败，请重试');
      console.error(error);
    } finally {
      setIsSubmitting(false);
      setConfirmDialog({ open: false, decision: null });
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-6 lg:grid-cols-3">
          <Skeleton className="h-[600px] lg:col-span-2" />
          <Skeleton className="h-[400px]" />
        </div>
      </div>
    );
  }

  if (!workflow) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <h2 className="text-lg font-medium">审核项不存在</h2>
        <Link href="/approvals" className="mt-4">
          <Button variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" />
            返回列表
          </Button>
        </Link>
      </div>
    );
  }

  const agentOutputs = state?.agent_outputs || workflow.output_data || {};

  return (
    <div>
      <PageHeader
        title="内容审核"
        description={`${WORKFLOW_TYPE_LABELS[workflow.workflow_type]} - 审核AI生成的内容`}
      >
        <Link href="/approvals">
          <Button variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" />
            返回
          </Button>
        </Link>
      </PageHeader>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Content Preview */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">生成内容预览</CardTitle>
              <CardDescription>
                审核以下AI生成的内容，确认无误后点击批准
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ContentPreview agentOutputs={agentOutputs} />
            </CardContent>
          </Card>
        </div>

        {/* Actions Panel */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">审核操作</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>审核意见（可选）</Label>
                <Textarea
                  placeholder="添加您的审核意见或修改建议..."
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  rows={4}
                />
              </div>

              <div className="flex flex-col gap-2">
                <Button
                  className="w-full bg-emerald-600 hover:bg-emerald-700"
                  onClick={() => setConfirmDialog({ open: true, decision: 'approve' })}
                  disabled={isSubmitting}
                >
                  <Check className="mr-2 h-4 w-4" />
                  批准
                </Button>

                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => setConfirmDialog({ open: true, decision: 'request_changes' })}
                  disabled={isSubmitting}
                >
                  <MessageSquare className="mr-2 h-4 w-4" />
                  请求修改
                </Button>

                <Button
                  variant="destructive"
                  className="w-full"
                  onClick={() => setConfirmDialog({ open: true, decision: 'reject' })}
                  disabled={isSubmitting}
                >
                  <X className="mr-2 h-4 w-4" />
                  拒绝
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">审核说明</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-2">
              <p><strong>批准</strong>：确认内容无误，继续执行后续流程</p>
              <p><strong>请求修改</strong>：需要AI根据您的意见重新生成</p>
              <p><strong>拒绝</strong>：终止当前工作流</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialog.open}
        onOpenChange={(open) => setConfirmDialog({ ...confirmDialog, open })}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              确认{confirmDialog.decision === 'approve' ? '批准' :
                   confirmDialog.decision === 'reject' ? '拒绝' : '请求修改'}
            </DialogTitle>
            <DialogDescription>
              {confirmDialog.decision === 'approve' && '确认批准后，系统将继续执行后续流程。'}
              {confirmDialog.decision === 'reject' && '确认拒绝后，当前工作流将终止。'}
              {confirmDialog.decision === 'request_changes' && '确认后，系统将根据您的意见重新生成内容。'}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setConfirmDialog({ open: false, decision: null })}
              disabled={isSubmitting}
            >
              取消
            </Button>
            <Button
              onClick={() => confirmDialog.decision && handleSubmit(confirmDialog.decision)}
              disabled={isSubmitting}
              className={
                confirmDialog.decision === 'approve'
                  ? 'bg-emerald-600 hover:bg-emerald-700'
                  : confirmDialog.decision === 'reject'
                  ? 'bg-destructive hover:bg-destructive/90'
                  : ''
              }
            >
              {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              确认
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
