import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import { FileCheck, ChevronRight } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { PendingApproval } from '@/lib/types';

interface ApprovalCardProps {
  approval: PendingApproval;
}

export function ApprovalCard({ approval }: ApprovalCardProps) {
  const timeAgo = formatDistanceToNow(new Date(approval.created_at), {
    addSuffix: true,
    locale: zhCN,
  });

  // Count items in preview
  const previewItems = Object.entries(approval.content_preview || {});

  return (
    <Card className="transition-all hover:shadow-md hover:border-foreground/20">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-amber-500/10">
              <FileCheck className="h-4 w-4 text-amber-600" />
            </div>
            <div>
              <div className="font-medium">{approval.agent_name}</div>
              <div className="text-xs text-muted-foreground">{approval.step_name}</div>
            </div>
          </div>
          <Badge variant="secondary" className="bg-amber-500/10 text-amber-600">
            待审核
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* Preview summary */}
          <div className="flex flex-wrap gap-2">
            {previewItems.slice(0, 3).map(([key, value]) => (
              <Badge key={key} variant="outline" className="text-xs">
                {key}: {String(value)}
              </Badge>
            ))}
          </div>

          <div className="flex items-center justify-between pt-2">
            <span className="text-sm text-muted-foreground">{timeAgo}</span>
            <Link href={`/approvals/${approval.workflow_id}`}>
              <Button size="sm">
                审核
                <ChevronRight className="ml-1 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
