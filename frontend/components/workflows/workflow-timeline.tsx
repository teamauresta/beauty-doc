'use client';

import { Check, Loader2, Circle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { AGENT_LABELS, AGENT_ORDER } from '@/lib/types';
import type { AgentType, WorkflowState } from '@/lib/types';

interface WorkflowTimelineProps {
  state?: WorkflowState;
  currentStep?: string;
  status: string;
}

const stepOrder = [
  ...AGENT_ORDER,
  'aggregate_results',
  'human_review',
  'execute_approved',
] as const;

const stepLabels: Record<string, string> = {
  ...AGENT_LABELS,
  aggregate_results: '汇总结果',
  human_review: '人工审核',
  execute_approved: '执行发布',
};

type StepStatus = 'completed' | 'current' | 'pending' | 'error';

function getStepStatus(
  step: string,
  currentStep?: string,
  workflowStatus?: string,
  agentOutputs?: Record<string, unknown>
): StepStatus {
  if (workflowStatus === 'failed') {
    if (step === currentStep) return 'error';
  }

  // Check if this agent has output
  if (agentOutputs && step in agentOutputs) {
    return 'completed';
  }

  if (step === currentStep) {
    return 'current';
  }

  // Check if current step is after this step in order
  const currentIndex = stepOrder.indexOf(currentStep as (typeof stepOrder)[number]);
  const stepIndex = stepOrder.indexOf(step as (typeof stepOrder)[number]);

  if (currentIndex > stepIndex) {
    return 'completed';
  }

  return 'pending';
}

function StepIcon({ status }: { status: StepStatus }) {
  switch (status) {
    case 'completed':
      return (
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500 text-white">
          <Check className="h-4 w-4" />
        </div>
      );
    case 'current':
      return (
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-500 text-white">
          <Loader2 className="h-4 w-4 animate-spin" />
        </div>
      );
    case 'error':
      return (
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-red-500 text-white">
          <AlertCircle className="h-4 w-4" />
        </div>
      );
    default:
      return (
        <div className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-muted bg-background">
          <Circle className="h-3 w-3 text-muted-foreground" />
        </div>
      );
  }
}

export function WorkflowTimeline({ state, currentStep, status }: WorkflowTimelineProps) {
  return (
    <div className="space-y-1">
      {stepOrder.map((step, index) => {
        const stepStatus = getStepStatus(step, currentStep, status, state?.agent_outputs);
        const isLast = index === stepOrder.length - 1;

        return (
          <div key={step} className="flex gap-4">
            <div className="flex flex-col items-center">
              <StepIcon status={stepStatus} />
              {!isLast && (
                <div
                  className={cn(
                    'w-0.5 flex-1 min-h-[24px]',
                    stepStatus === 'completed' ? 'bg-emerald-500' : 'bg-muted'
                  )}
                />
              )}
            </div>
            <div className="flex-1 pb-6">
              <div
                className={cn(
                  'font-medium',
                  stepStatus === 'pending' && 'text-muted-foreground'
                )}
              >
                {stepLabels[step] || step}
              </div>
              {stepStatus === 'current' && (
                <div className="mt-1 text-sm text-muted-foreground">处理中...</div>
              )}
              {stepStatus === 'error' && (
                <div className="mt-1 text-sm text-red-500">执行失败</div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
