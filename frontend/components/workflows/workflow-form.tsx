'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Loader2, ChevronRight, ChevronLeft, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useTenants } from '@/lib/hooks';
import { createWorkflow } from '@/lib/api';
import type { WorkflowType, WorkflowCreate } from '@/lib/types';
import { WORKFLOW_TYPE_LABELS } from '@/lib/types';

const workflowTypes: { value: WorkflowType; description: string }[] = [
  { value: 'full_growth_plan', description: '完整30/60/90天增长策略，包含所有模块' },
  { value: 'content_generation', description: '生成爆款选题、品牌栏目和内容脚本' },
  { value: 'influencer_matching', description: '筛选和匹配适合的KOL博主' },
  { value: 'community_strategy', description: '社群运营话术和转化策略' },
  { value: 'product_strategy', description: '产品定价和组合策略建议' },
];

export function WorkflowForm() {
  const router = useRouter();
  const { data: tenants, isLoading: tenantsLoading } = useTenants();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  const [formData, setFormData] = useState({
    tenant_id: '',
    workflow_type: '' as WorkflowType | '',
    institution_info: {
      name: '',
      city: '',
      tier: 'medium' as 'high' | 'medium' | 'low',
      main_services: [] as string[],
      target_audience: '',
    },
    auto_approve: false,
  });

  const handleSubmit = async () => {
    if (!formData.tenant_id || !formData.workflow_type) {
      toast.error('请选择机构和任务类型');
      return;
    }

    setIsLoading(true);
    try {
      const payload: WorkflowCreate = {
        tenant_id: formData.tenant_id,
        workflow_type: formData.workflow_type as WorkflowType,
        input_data: {
          institution_info: formData.institution_info,
        },
        auto_approve: formData.auto_approve,
      };

      const workflow = await createWorkflow(payload);
      toast.success('工作流已创建');
      router.push(`/workflows/${workflow.id}`);
    } catch (error) {
      toast.error('创建失败，请重试');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const selectedTenant = tenants?.find((t) => t.id === formData.tenant_id);

  // Auto-fill institution info from tenant
  const handleTenantSelect = (tenantId: string) => {
    const tenant = tenants?.find((t) => t.id === tenantId);
    if (tenant) {
      setFormData({
        ...formData,
        tenant_id: tenantId,
        institution_info: {
          name: tenant.name,
          city: tenant.city,
          tier: (tenant.tier as 'high' | 'medium' | 'low') || 'medium',
          main_services: tenant.main_services || [],
          target_audience: tenant.target_audience || '',
        },
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Progress indicator */}
      <div className="flex items-center gap-2">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex items-center gap-2">
            <div
              className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium transition-colors ${
                s === step
                  ? 'bg-foreground text-background'
                  : s < step
                  ? 'bg-emerald-500 text-white'
                  : 'bg-muted text-muted-foreground'
              }`}
            >
              {s}
            </div>
            {s < 3 && (
              <div className={`h-0.5 w-8 ${s < step ? 'bg-emerald-500' : 'bg-muted'}`} />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Select Tenant */}
      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>选择机构</CardTitle>
            <CardDescription>选择要为哪个机构创建增长计划</CardDescription>
          </CardHeader>
          <CardContent>
            <Select
              value={formData.tenant_id}
              onValueChange={handleTenantSelect}
              disabled={tenantsLoading}
            >
              <SelectTrigger>
                <SelectValue placeholder={tenantsLoading ? '加载中...' : '选择机构'} />
              </SelectTrigger>
              <SelectContent>
                {tenants?.map((tenant) => (
                  <SelectItem key={tenant.id} value={tenant.id}>
                    {tenant.name} - {tenant.city}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {tenants?.length === 0 && (
              <p className="mt-2 text-sm text-muted-foreground">
                暂无机构，请先添加机构
              </p>
            )}
          </CardContent>
          <CardFooter className="justify-end">
            <Button onClick={() => setStep(2)} disabled={!formData.tenant_id}>
              下一步
              <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* Step 2: Select Workflow Type */}
      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle>选择任务类型</CardTitle>
            <CardDescription>选择您需要的增长策略类型</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {workflowTypes.map((wt) => (
              <div
                key={wt.value}
                onClick={() => setFormData({ ...formData, workflow_type: wt.value })}
                className={`cursor-pointer rounded-lg border p-4 transition-all ${
                  formData.workflow_type === wt.value
                    ? 'border-foreground bg-accent'
                    : 'hover:border-foreground/50'
                }`}
              >
                <div className="font-medium">{WORKFLOW_TYPE_LABELS[wt.value]}</div>
                <div className="mt-1 text-sm text-muted-foreground">{wt.description}</div>
              </div>
            ))}
          </CardContent>
          <CardFooter className="justify-between">
            <Button variant="outline" onClick={() => setStep(1)}>
              <ChevronLeft className="mr-2 h-4 w-4" />
              上一步
            </Button>
            <Button onClick={() => setStep(3)} disabled={!formData.workflow_type}>
              下一步
              <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* Step 3: Review & Submit */}
      {step === 3 && (
        <Card>
          <CardHeader>
            <CardTitle>确认并开始</CardTitle>
            <CardDescription>确认以下信息后开始生成</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg bg-muted p-4 space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">机构</span>
                <span className="font-medium">{selectedTenant?.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">城市</span>
                <span>{selectedTenant?.city}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">任务类型</span>
                <span className="font-medium">
                  {formData.workflow_type && WORKFLOW_TYPE_LABELS[formData.workflow_type]}
                </span>
              </div>
            </div>

            {/* Additional context */}
            <div className="space-y-2">
              <Label>补充说明（可选）</Label>
              <Textarea
                placeholder="添加任何额外的要求或上下文..."
                value={formData.institution_info.target_audience}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    institution_info: {
                      ...formData.institution_info,
                      target_audience: e.target.value,
                    },
                  })
                }
                rows={3}
              />
            </div>
          </CardContent>
          <CardFooter className="justify-between">
            <Button variant="outline" onClick={() => setStep(2)}>
              <ChevronLeft className="mr-2 h-4 w-4" />
              上一步
            </Button>
            <Button onClick={handleSubmit} disabled={isLoading}>
              {isLoading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="mr-2 h-4 w-4" />
              )}
              开始生成
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  );
}
