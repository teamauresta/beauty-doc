'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { AGENT_LABELS } from '@/lib/types';
import type { AgentType } from '@/lib/types';

interface AgentOutputViewerProps {
  outputs: Record<string, unknown>;
}

function OutputSection({ title, data }: { title: string; data: unknown }) {
  if (!data) return null;

  if (Array.isArray(data)) {
    return (
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{title}</span>
          <Badge variant="secondary">{data.length} 项</Badge>
        </div>
        <ScrollArea className="h-[200px] rounded-md border p-3">
          <pre className="text-xs">{JSON.stringify(data, null, 2)}</pre>
        </ScrollArea>
      </div>
    );
  }

  if (typeof data === 'object') {
    return (
      <div className="space-y-2">
        <span className="text-sm font-medium">{title}</span>
        <ScrollArea className="h-[200px] rounded-md border p-3">
          <pre className="text-xs">{JSON.stringify(data, null, 2)}</pre>
        </ScrollArea>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-muted-foreground">{title}</span>
      <span className="text-sm">{String(data)}</span>
    </div>
  );
}

export function AgentOutputViewer({ outputs }: AgentOutputViewerProps) {
  const agentKeys = Object.keys(outputs).filter(
    (key) => key !== 'error' && outputs[key]
  );

  if (agentKeys.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        暂无输出结果
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {agentKeys.map((agentKey) => {
        const agentLabel = AGENT_LABELS[agentKey as AgentType] || agentKey;
        const output = outputs[agentKey] as Record<string, unknown>;
        const isObject = output && typeof output === 'object';
        const hasError = isObject && 'error' in output && output.error;

        return (
          <Card key={agentKey}>
            <CardHeader className="py-3">
              <CardTitle className="text-base flex items-center gap-2">
                {agentLabel}
                {isObject && !hasError ? (
                  <Badge variant="secondary" className="bg-emerald-500/10 text-emerald-600">
                    完成
                  </Badge>
                ) : null}
                {hasError ? (
                  <Badge variant="destructive">错误</Badge>
                ) : null}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {isObject ? (
                Object.entries(output).map(([key, value]) => (
                  <OutputSection key={key} title={key} data={value} />
                ))
              ) : (
                <pre className="text-xs">{JSON.stringify(output, null, 2)}</pre>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
