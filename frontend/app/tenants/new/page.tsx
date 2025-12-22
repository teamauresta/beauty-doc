import { PageHeader } from '@/components/layout/page-header';
import { TenantForm } from '@/components/tenants/tenant-form';

export default function NewTenantPage() {
  return (
    <div className="max-w-2xl">
      <PageHeader title="添加机构" description="填写新机构的基本信息" />
      <TenantForm />
    </div>
  );
}
