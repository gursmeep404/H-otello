'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { MessageCircle, Send, Clock, Sparkles } from 'lucide-react';

// Type definitions
interface QueryResponse {
  query: string;
}

interface ApiResponse {
  query?: string;
}

interface SubmitPayload {
  query: string | null;
  response: string;
}

const App: React.FC = () => {
  const [query, setQuery] = useState<string | null>(null);
  const [response, setResponse] = useState<string>('');

  useEffect(() => {
    const fetchQuery = async (): Promise<void> => {
      try {
        const res = await fetch('http://127.0.0.1:8000/api/query');
        const data: ApiResponse = await res.json();
        if (data.query) setQuery(data.query);
      } catch (error) {
        console.error('Error fetching query:', error);
      }
    };

    const interval = setInterval(fetchQuery, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = async (): Promise<void> => {
    if (!response.trim()) return;

    try {
      const payload: SubmitPayload = { query, response };
      await fetch('http://127.0.0.1:8000/api/respond', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      setQuery(null);
      setResponse('');
    } catch (error) {
      console.error('Error submitting response:', error);
    }
  };

  const handleTextareaChange = (
    e: React.ChangeEvent<HTMLTextAreaElement>
  ): void => {
    setResponse(e.target.value);
  };

  return (
    <div className='min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-4'>
      <div className='max-w-4xl mx-auto pt-8'>
        {/* Header */}
        <div className='text-center mb-8'>
          <div className='flex items-center justify-center gap-3 mb-4'>
            <div className='p-2 bg-blue-600 rounded-lg'>
              <Sparkles className='w-6 h-6 text-white' />
            </div>
            <h1 className='text-4xl font-bold text-blue-800'>
              Query Resolution Dashboard
            </h1>
          </div>
          <p className='text-gray-600 text-lg'>
            Assist AI with human expertise when needed
          </p>
        </div>

        {/* Main Content */}
        <Card className='shadow-xl border bg-white'>
          <CardHeader className='pb-4'>
            <div className='flex items-center justify-between'>
              <CardTitle className='text-xl text-gray-800 flex items-center gap-2'>
                <MessageCircle className='w-5 h-5 text-blue-600' />
                Current Query
              </CardTitle>
              {query && (
                <Badge
                  variant='secondary'
                  className='bg-amber-100 text-amber-800 border-amber-200'
                >
                  <Clock className='w-3 h-3 mr-1' />
                  Awaiting Response
                </Badge>
              )}
            </div>
          </CardHeader>

          <CardContent className='space-y-6'>
            {query ? (
              <>
                {/* Query Display */}
                <div className='space-y-3'>
                  <div className='flex items-center gap-2'>
                    <span className='text-sm font-medium text-gray-700'>
                      Incoming Query:
                    </span>
                    <Badge variant='outline' className='text-xs'>
                      From AI Assistant
                    </Badge>
                  </div>
                  <div className='bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 p-4 rounded-lg'>
                    <p className='text-gray-800 leading-relaxed font-medium'>
                      {query}
                    </p>
                  </div>
                </div>

                {/* Response Input */}
                <div className='space-y-3'>
                  <label className='text-sm font-medium text-gray-700'>
                    Your Expert Response:
                  </label>
                  <Textarea
                    placeholder='Provide a detailed, helpful response to assist the AI...'
                    value={response}
                    onChange={handleTextareaChange}
                    className='min-h-32 resize-none border-gray-200 focus:border-blue-500 focus:ring-blue-500'
                  />
                  <div className='flex items-center justify-between'>
                    <span className='text-xs text-gray-500'>
                      {response.length} characters
                    </span>
                    <Button
                      onClick={handleSubmit}
                      disabled={!response.trim()}
                      className='bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium px-6 py-2 rounded-lg transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none'
                    >
                      <Send className='w-4 h-4 mr-2' />
                      Send Response
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <div className='text-center py-16'>
                <div className='mb-6'>
                  <div className='w-16 h-16 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4'>
                    <MessageCircle className='w-8 h-8 text-blue-600' />
                  </div>
                  <h3 className='text-xl font-semibold text-gray-700 mb-2'>
                    All Caught Up!
                  </h3>
                  <p className='text-gray-500 max-w-md mx-auto'>
                    No queries to answer at the moment. The system will
                    automatically fetch new queries that need your expertise.
                  </p>
                </div>
                <div className='flex items-center justify-center gap-2 text-sm text-gray-400'>
                  <div className='w-2 h-2 bg-green-400 rounded-full animate-pulse'></div>
                  <span>Listening for new queries...</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Footer */}
        <div className='text-center mt-8 text-gray-500 text-sm'>
          <p>System checks for new queries every 3 seconds</p>
        </div>
      </div>
    </div>
  );
};

export default App;
