'use client';

import { use } from 'react';
import Link from 'next/link';
import { ArrowLeft, RefreshCw, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { PageHeader } from '@/components/layout/page-header';
import { WorkflowStatusBadge } from '@/components/workflows/workflow-status-badge';
import { WorkflowTimeline } from '@/components/workflows/workflow-timeline';
import { AgentOutputViewer } from '@/components/workflows/agent-output-viewer';
import { useWorkflow, useWorkflowState } from '@/lib/hooks';
import { WORKFLOW_TYPE_LABELS } from '@/lib/types';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function WorkflowDetailPage({ params }: PageProps) {
  const { id } = use(params);
  const { workflow, isLoading, isError, mutate } = useWorkflow(id);
  const { state } = useWorkflowState(id);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-6 lg:grid-cols-3">
          <Skeleton className="h-[400px] lg:col-span-1" />
          <Skeleton className="h-[400px] lg:col-span-2" />
        </div>
      </div>
    );
  }

  if (isError || !workflow) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <h2 className="text-lg font-medium">工作流不存在</h2>
        <p className="mt-1 text-muted-foreground">无法找到该工作流</p>
        <Link href="/workflows" className="mt-4">
          <Button variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" />
            返回列表
          </Button>
        </Link>
      </div>
    );
  }

  const showApprovalButton = workflow.status === 'awaiting_approval';

  return (
    <div>
      <PageHeader
        title={WORKFLOW_TYPE_LABELS[workflow.workflow_type]}
        description={`创建于 ${new Date(workflow.created_at).toLocaleString('zh-CN')}`}
      >
        <div className="flex items-center gap-2">
          <WorkflowStatusBadge status={workflow.status} />
          <Button variant="outline" size="icon" onClick={() => mutate()}>
            <RefreshCw className="h-4 w-4" />
          </Button>
          {showApprovalButton && (
            <Link href={`/approvals/${workflow.id}`}>
              <Button>
                <ExternalLink className="mr-2 h-4 w-4" />
                审核
              </Button>
            </Link>
          )}
        </div>
      </PageHeader>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Timeline */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-base">执行进度</CardTitle>
          </CardHeader>
          <CardContent>
            <WorkflowTimeline
              state={state}
              currentStep={workflow.current_step}
              status={workflow.status}
            />
          </CardContent>
        </Card>

        {/* Details */}
        <div className="lg:col-span-2">
          <Tabs defaultValue="outputs">
            <TabsList>
              <TabsTrigger value="outputs">输出结果</TabsTrigger>
              <TabsTrigger value="input">输入数据</TabsTrigger>
              <TabsTrigger value="state">状态详情</TabsTrigger>
            </TabsList>

            <TabsContent value="outputs" className="mt-4">
              {state?.agent_outputs ? (
                <AgentOutputViewer outputs={state.agent_outputs} />
              ) : workflow.output_data ? (
                <AgentOutputViewer outputs={workflow.output_data} />
              ) : (
                <Card>
                  <CardContent className="py-8 text-center text-muted-foreground">
                    {workflow.status === 'running' || workflow.status === 'pending'
                      ? '正在处理中...'
                      : '暂无输出结果'}
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="input" className="mt-4">
              <Card>
                <CardContent className="pt-6">
                  <pre className="overflow-auto rounded-md bg-muted p-4 text-sm">
                    {JSON.stringify(workflow.input_data, null, 2)}
                  </pre>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="state" className="mt-4">
              <Card>
                <CardContent className="pt-6">
                  <pre className="overflow-auto rounded-md bg-muted p-4 text-sm">
                    {JSON.stringify(state || {}, null, 2)}
                  </pre>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
