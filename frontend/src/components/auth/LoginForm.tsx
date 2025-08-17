/**
 * 로그인 폼 컴포넌트
 */

'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2 } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';

export function LoginForm() {
  const { login, register, isLoading } = useAuthStore();
  const [error, setError] = useState<string>('');
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      if (isRegisterMode) {
        const success = await register(formData.name, formData.email, formData.password);
        if (success) {
          setIsRegisterMode(false);
          setFormData({ email: formData.email, password: '', name: '' });
          alert('회원가입이 완료되었습니다. 로그인해주세요.');
        }
      } else {
        const success = await login(formData.email, formData.password);
        if (!success) {
          setError('로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.');
        }
      }
    } catch (err: unknown) {
      setError((err as Error)?.message || (isRegisterMode ? '회원가입에 실패했습니다.' : '로그인에 실패했습니다.'));
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="text-center">
        <CardTitle>{isRegisterMode ? '회원가입' : '로그인'}</CardTitle>
        <CardDescription>
          포트폴리오 매니저에 {isRegisterMode ? '가입하세요' : '로그인하세요'}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegisterMode && (
            <div className="space-y-2">
              <Label htmlFor="name">이름</Label>
              <Input
                id="name"
                name="name"
                type="text"
                placeholder="홍길동"
                value={formData.name}
                onChange={handleInputChange}
                required
                disabled={isLoading}
              />
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="email">이메일</Label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="your-email@example.com"
              value={formData.email}
              onChange={handleInputChange}
              required
              disabled={isLoading}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">비밀번호</Label>
            <Input
              id="password"
              name="password"
              type="password"
              placeholder="비밀번호를 입력하세요"
              value={formData.password}
              onChange={handleInputChange}
              required
              disabled={isLoading}
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={isLoading}
          >
            {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            {isRegisterMode ? '회원가입' : '로그인'}
          </Button>
        </form>

        <div className="text-center">
          <Button
            type="button"
            variant="link"
            onClick={() => setIsRegisterMode(!isRegisterMode)}
            disabled={isLoading}
          >
            {isRegisterMode ? '이미 계정이 있으신가요? 로그인' : '계정이 없으신가요? 회원가입'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}