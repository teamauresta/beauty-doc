import { PageHeader } from '@/components/layout/page-header';
import { WorkflowForm } from '@/components/workflows/workflow-form';

export default function NewWorkflowPage() {
  return (
    <div className="max-w-2xl">
      <PageHeader title="创建任务" description="为您的机构创建新的增长任务" />
      <WorkflowForm />
    </div>
  );
}
