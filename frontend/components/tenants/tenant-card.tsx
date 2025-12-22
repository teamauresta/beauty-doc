import Link from 'next/link';
import { Building2, MapPin } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Tenant } from '@/lib/types';

interface TenantCardProps {
  tenant: Tenant;
}

const tierColors = {
  high: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
  medium: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
  low: 'bg-slate-500/10 text-slate-600 dark:text-slate-400',
};

const tierLabels = {
  high: '高端',
  medium: '中端',
  low: '标准',
};

export function TenantCard({ tenant }: TenantCardProps) {
  return (
    <Link href={`/tenants/${tenant.id}`}>
      <Card className="cursor-pointer transition-all hover:shadow-md hover:border-foreground/20">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-md bg-muted">
                <Building2 className="h-4 w-4" />
              </div>
              <CardTitle className="text-base">{tenant.name}</CardTitle>
            </div>
            <Badge
              variant="secondary"
              className={tierColors[tenant.tier as keyof typeof tierColors] || tierColors.medium}
            >
              {tierLabels[tenant.tier as keyof typeof tierLabels] || tenant.tier}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <MapPin className="h-3.5 w-3.5" />
            <span>{tenant.city}</span>
          </div>
          {tenant.main_services && tenant.main_services.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              {tenant.main_services.slice(0, 3).map((service, i) => (
                <Badge key={i} variant="outline" className="text-xs">
                  {service}
                </Badge>
              ))}
              {tenant.main_services.length > 3 && (
                <Badge variant="outline" className="text-xs">
                  +{tenant.main_services.length - 3}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
