'use client';

import Link from 'next/link';
import { Plus, Building2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { PageHeader } from '@/components/layout/page-header';
import { TenantCard } from '@/components/tenants/tenant-card';
import { useTenants } from '@/lib/hooks';

export default function TenantsPage() {
  const { data: tenants, isLoading, error } = useTenants();

  return (
    <div>
      <PageHeader title="机构管理" description="管理您的医美机构信息">
        <Link href="/tenants/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            添加机构
          </Button>
        </Link>
      </PageHeader>

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-[140px] rounded-lg" />
          ))}
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
          加载失败，请刷新页面重试
        </div>
      )}

      {tenants && tenants.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-16">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
            <Building2 className="h-6 w-6 text-muted-foreground" />
          </div>
          <h3 className="mt-4 text-lg font-medium">暂无机构</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            添加您的第一个医美机构开始使用
          </p>
          <Link href="/tenants/new" className="mt-4">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              添加机构
            </Button>
          </Link>
        </div>
      )}

      {tenants && tenants.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {tenants.map((tenant) => (
            <TenantCard key={tenant.id} tenant={tenant} />
          ))}
        </div>
      )}
    </div>
  );
}
