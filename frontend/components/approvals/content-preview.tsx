'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import type { ViralTopic, BrandColumn, ContentFactoryOutput } from '@/lib/types';

interface ContentPreviewProps {
  agentOutputs: Record<string, unknown>;
}

function ViralTopicCard({ topic }: { topic: ViralTopic }) {
  const platformColors: Record<string, string> = {
    xiaohongshu: 'bg-red-500/10 text-red-600',
    douyin: 'bg-black/10 text-black dark:bg-white/10 dark:text-white',
    weixin: 'bg-green-500/10 text-green-600',
  };

  return (
    <div className="rounded-lg border p-4 space-y-2">
      <div className="flex items-center gap-2">
        <Badge className={platformColors[topic.platform] || 'bg-muted'}>
          {topic.platform === 'xiaohongshu' ? '小红书' :
           topic.platform === 'douyin' ? '抖音' : '微信'}
        </Badge>
      </div>
      <h4 className="font-medium">{topic.title}</h4>
      <p className="text-sm text-muted-foreground">{topic.hook}</p>
      {topic.script_outline && topic.script_outline.length > 0 && (
        <div className="space-y-1">
          <span className="text-xs font-medium text-muted-foreground">脚本大纲</span>
          <ul className="text-sm list-disc list-inside text-muted-foreground">
            {topic.script_outline.slice(0, 3).map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function BrandColumnCard({ column }: { column: BrandColumn }) {
  return (
    <div className="rounded-lg border p-4 space-y-2">
      <h4 className="font-medium">{column.column_name}</h4>
      <p className="text-sm text-muted-foreground">{column.positioning}</p>
      <div className="flex flex-wrap gap-1">
        {column.sample_topics?.slice(0, 3).map((topic, i) => (
          <Badge key={i} variant="outline" className="text-xs">
            {topic}
          </Badge>
        ))}
      </div>
    </div>
  );
}

function ContentFactorySection({ data }: { data: ContentFactoryOutput }) {
  const viralTopics = data.viral_topics || [];
  const brandColumns = data.brand_columns || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          内容工厂
          <Badge variant="secondary">{viralTopics.length} 选题</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {viralTopics.length > 0 && (
          <div className="space-y-3">
            <h5 className="text-sm font-medium">爆款选题</h5>
            <div className="grid gap-3 sm:grid-cols-2">
              {viralTopics.slice(0, 4).map((topic, i) => (
                <ViralTopicCard key={i} topic={topic} />
              ))}
            </div>
          </div>
        )}

        {viralTopics.length > 0 && brandColumns.length > 0 && <Separator />}

        {brandColumns.length > 0 && (
          <div className="space-y-3">
            <h5 className="text-sm font-medium">品牌栏目</h5>
            <div className="grid gap-3 sm:grid-cols-2">
              {brandColumns.slice(0, 4).map((column, i) => (
                <BrandColumnCard key={i} column={column} />
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function JsonCard({ title, data }: { title: string; data: unknown }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <pre className="text-xs overflow-auto bg-muted rounded-md p-3">
          {JSON.stringify(data, null, 2)}
        </pre>
      </CardContent>
    </Card>
  );
}

export function ContentPreview({ agentOutputs }: ContentPreviewProps) {
  const contentFactory = agentOutputs.content_factory as ContentFactoryOutput | undefined;
  const communityOps = agentOutputs.community_ops;
  const influencer = agentOutputs.influencer_matching;
  const product = agentOutputs.product_strategy;

  const otherKeys = Object.keys(agentOutputs).filter(
    (k) => !['content_factory', 'community_ops', 'influencer_matching', 'product_strategy'].includes(k)
  );

  return (
    <ScrollArea className="h-[600px] pr-4">
      <div className="space-y-6">
        {contentFactory ? <ContentFactorySection data={contentFactory} /> : null}
        {communityOps ? <JsonCard title="社群运营" data={communityOps} /> : null}
        {influencer ? <JsonCard title="博主匹配" data={influencer} /> : null}
        {product ? <JsonCard title="产品策略" data={product} /> : null}
        {otherKeys.length > 0 ? (
          <JsonCard
            title="其他输出"
            data={Object.fromEntries(otherKeys.map((k) => [k, agentOutputs[k]]))}
          />
        ) : null}
      </div>
    </ScrollArea>
  );
}
