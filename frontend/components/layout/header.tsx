'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTheme } from 'next-themes';
import { Moon, Sun, Workflow, CheckCircle, Building2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { usePendingApprovals } from '@/lib/hooks';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Workflows', href: '/workflows', icon: Workflow },
  { name: 'Approvals', href: '/approvals', icon: CheckCircle },
  { name: 'Tenants', href: '/tenants', icon: Building2 },
];

export function Header() {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const { data: approvals } = usePendingApprovals();

  const pendingCount = approvals?.length || 0;

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 max-w-screen-2xl items-center">
        {/* Logo */}
        <Link href="/" className="mr-6 flex items-center space-x-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-md bg-foreground text-background">
            <span className="text-xs font-bold">B</span>
          </div>
          <span className="hidden font-semibold sm:inline-block">
            Beauty Growth
          </span>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-1">
          {navigation.map((item) => {
            const isActive = pathname.startsWith(item.href);
            const Icon = item.icon;

            return (
              <Link key={item.href} href={item.href}>
                <Button
                  variant="ghost"
                  size="sm"
                  className={cn(
                    'gap-2 text-muted-foreground hover:text-foreground',
                    isActive && 'bg-accent text-foreground'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{item.name}</span>
                  {item.href === '/approvals' && pendingCount > 0 && (
                    <Badge
                      variant="secondary"
                      className="ml-1 h-5 min-w-[20px] px-1.5 text-xs"
                    >
                      {pendingCount}
                    </Badge>
                  )}
                </Button>
              </Link>
            );
          })}
        </nav>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Theme toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="h-9 w-9"
        >
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </div>
    </header>
  );
}
