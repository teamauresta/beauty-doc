'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Loader2, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { createTenant } from '@/lib/api';
import type { TenantCreate } from '@/lib/types';

const tierOptions = [
  { value: 'high', label: '高端', description: '高客单价，高端医美' },
  { value: 'medium', label: '中端', description: '中等客单价，综合医美' },
  { value: 'low', label: '标准', description: '标准客单价，轻医美' },
] as const;

export function TenantForm() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<TenantCreate>({
    name: '',
    city: '',
    tier: 'medium',
    main_services: [],
    target_audience: '',
    competitors: [],
  });
  const [serviceInput, setServiceInput] = useState('');
  const [competitorInput, setCompetitorInput] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.city) {
      toast.error('请填写必填字段');
      return;
    }

    setIsLoading(true);
    try {
      await createTenant(formData);
      toast.success('机构创建成功');
      router.push('/tenants');
      router.refresh();
    } catch (error) {
      toast.error('创建失败，请重试');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const addService = () => {
    if (serviceInput.trim()) {
      setFormData({
        ...formData,
        main_services: [...formData.main_services, serviceInput.trim()],
      });
      setServiceInput('');
    }
  };

  const removeService = (index: number) => {
    setFormData({
      ...formData,
      main_services: formData.main_services.filter((_, i) => i !== index),
    });
  };

  const addCompetitor = () => {
    if (competitorInput.trim()) {
      setFormData({
        ...formData,
        competitors: [...(formData.competitors || []), competitorInput.trim()],
      });
      setCompetitorInput('');
    }
  };

  const removeCompetitor = (index: number) => {
    setFormData({
      ...formData,
      competitors: (formData.competitors || []).filter((_, i) => i !== index),
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <Card>
        <CardHeader>
          <CardTitle>机构信息</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Name & City */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="name">机构名称 *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="例如：美丽医美"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="city">所在城市 *</Label>
              <Input
                id="city"
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                placeholder="例如：上海"
              />
            </div>
          </div>

          {/* Tier */}
          <div className="space-y-2">
            <Label>客单价层级</Label>
            <div className="grid gap-2 sm:grid-cols-3">
              {tierOptions.map((option) => (
                <div
                  key={option.value}
                  onClick={() => setFormData({ ...formData, tier: option.value })}
                  className={`cursor-pointer rounded-lg border p-3 transition-all ${
                    formData.tier === option.value
                      ? 'border-foreground bg-accent'
                      : 'hover:border-foreground/50'
                  }`}
                >
                  <div className="font-medium">{option.label}</div>
                  <div className="text-xs text-muted-foreground">{option.description}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Main Services */}
          <div className="space-y-2">
            <Label>主打项目</Label>
            <div className="flex gap-2">
              <Input
                value={serviceInput}
                onChange={(e) => setServiceInput(e.target.value)}
                placeholder="添加项目，如：水光针"
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addService())}
              />
              <Button type="button" variant="secondary" onClick={addService}>
                添加
              </Button>
            </div>
            {formData.main_services.length > 0 && (
              <div className="flex flex-wrap gap-1 pt-2">
                {formData.main_services.map((service, i) => (
                  <Badge key={i} variant="secondary" className="gap-1 pr-1">
                    {service}
                    <button
                      type="button"
                      onClick={() => removeService(i)}
                      className="ml-1 rounded-full hover:bg-foreground/10"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Target Audience */}
          <div className="space-y-2">
            <Label htmlFor="audience">目标客群</Label>
            <Textarea
              id="audience"
              value={formData.target_audience || ''}
              onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
              placeholder="描述您的目标客户画像..."
              rows={3}
            />
          </div>

          {/* Competitors */}
          <div className="space-y-2">
            <Label>竞争对手</Label>
            <div className="flex gap-2">
              <Input
                value={competitorInput}
                onChange={(e) => setCompetitorInput(e.target.value)}
                placeholder="添加竞品机构名称"
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCompetitor())}
              />
              <Button type="button" variant="secondary" onClick={addCompetitor}>
                添加
              </Button>
            </div>
            {formData.competitors && formData.competitors.length > 0 && (
              <div className="flex flex-wrap gap-1 pt-2">
                {formData.competitors.map((comp, i) => (
                  <Badge key={i} variant="outline" className="gap-1 pr-1">
                    {comp}
                    <button
                      type="button"
                      onClick={() => removeCompetitor(i)}
                      className="ml-1 rounded-full hover:bg-foreground/10"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>
        </CardContent>
        <CardFooter className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={() => router.back()}>
            取消
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            创建机构
          </Button>
        </CardFooter>
      </Card>
    </form>
  );
}
